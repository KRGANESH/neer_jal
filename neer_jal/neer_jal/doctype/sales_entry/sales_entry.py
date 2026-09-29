# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate

from neer_jal.api.sms import queue_delivery_sms
from neer_jal.neer_jal.utils import update_customer_balance, update_trip_cans_delivered


class SalesEntry(Document):
	def validate(self):
		self.cans_returned = cint(self.cans_returned)
		self.apply_can_exchange_rules()
		# Free cans (e.g. promotional/goodwill deliveries) never generate revenue,
		# regardless of the can count or rate.
		self.amount = 0 if self.payment_mode == "Free" else flt(self.cans_given) * flt(self.rate_per_can)

		if self.is_new() and not self.trip:
			self.link_active_trip()

		if self.is_new() and self.trip:
			self.validate_trip_date()

		self.validate_trip_capacity()

	def apply_can_exchange_rules(self):
		customer = frappe.db.get_value(
			"Customer", self.customer, ["cans_required", "cans_pending"], as_dict=True
		)
		target = cint(customer.cans_required)
		current_pending = cint(customer.cans_pending)

		if self.cans_returned > current_pending:
			frappe.throw(
				f"Refill ({self.cans_returned}) cannot exceed the {current_pending} can(s) "
				f"this customer currently holds"
			)

		# Always top up (or draw down) to the customer's current target can count.
		# This keeps working correctly even if a manager changes the customer's
		# cans_required after deliveries have already started.
		self.cans_given = max(0, target - current_pending + self.cans_returned)

	def link_active_trip(self):
		active_trip = frappe.db.get_value(
			"Trip", {"driver": self.sales_person, "status": "Active"}, "name"
		)
		if active_trip:
			self.trip = active_trip
			return

		roles = frappe.get_roles(self.sales_person)
		if not ({"Sales Manager", "System Manager"} & set(roles)):
			frappe.throw(
				"You don't have an active trip. Please start a trip before recording a delivery."
			)

	def validate_trip_date(self):
		trip_start = frappe.db.get_value("Trip", self.trip, "start_time")
		if not trip_start:
			return

		entry_date = getdate(self.sales_date) if self.sales_date else getdate()
		if getdate(trip_start) != entry_date:
			frappe.throw(
				"This trip was started on a different day. Please close the current trip "
				"and start a new one before recording today's deliveries. Trips should be "
				"closed on the same day they are started."
			)

	def validate_trip_capacity(self):
		if not self.trip:
			return

		trip = frappe.db.get_value("Trip", self.trip, ["cans_loaded", "cans_delivered"], as_dict=True)
		if not trip:
			return

		already_delivered = flt(trip.cans_delivered)
		if not self.is_new():
			previous = self.get_doc_before_save()
			if previous:
				already_delivered -= flt(previous.cans_given)

		if already_delivered + flt(self.cans_given) > flt(trip.cans_loaded):
			remaining = flt(trip.cans_loaded) - already_delivered
			frappe.throw(
				f"Not enough cans loaded on this trip. Only {remaining:g} can(s) remaining "
				f"out of {trip.cans_loaded:g} loaded."
			)

	def on_update(self):
		update_customer_balance(self.customer)
		previous = self.get_doc_before_save()
		if previous and previous.customer and previous.customer != self.customer:
			update_customer_balance(previous.customer)

		if self.trip:
			update_trip_cans_delivered(self.trip)
		if previous and previous.trip and previous.trip != self.trip:
			update_trip_cans_delivered(previous.trip)

	def after_insert(self):
		queue_delivery_sms(self.name)

	def after_delete(self):
		update_customer_balance(self.customer)
		if self.trip:
			update_trip_cans_delivered(self.trip)
