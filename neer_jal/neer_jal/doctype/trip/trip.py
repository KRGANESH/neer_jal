# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, now_datetime


class Trip(Document):
	def before_insert(self):
		if "Sales User" not in frappe.get_roles():
			frappe.throw("Only a driver login can start a trip")

		self.driver = frappe.session.user
		self.sales_person = self.driver
		if not self.trip_route:
			frappe.throw("Please select a trip route")

		route = frappe.db.get_value(
			"Trip Route", self.trip_route, ["route_price", "disabled"], as_dict=True
		)
		if not route or route.disabled:
			frappe.throw("Please select an active trip route")
		self.route_price = flt(route.route_price)

		existing = frappe.db.get_value(
			"Trip", {"driver": self.driver, "status": "Active"}, "name"
		)
		if existing:
			frappe.throw(
				f"{self.driver} already has an active trip ({existing}). "
				"Please close it before starting a new one."
			)

		last_end_km = frappe.db.get_value(
			"Trip",
			{"vehicle": self.vehicle, "status": "Completed"},
			"end_km",
			order_by="end_time desc",
		)
		if last_end_km is not None and flt(self.start_km) < flt(last_end_km):
			frappe.throw(
				f"Starting KM ({self.start_km}) cannot be less than this vehicle's last "
				f"trip ending KM ({last_end_km})"
			)

	def validate(self):
		previous = self.get_doc_before_save() if not self.is_new() else None
		if previous:
			if previous.status == "Completed" and not self.end_km:
				frappe.throw("A completed trip cannot be reopened")
			self.driver = previous.driver
			self.trip_route = previous.trip_route
			self.route_price = previous.route_price

		if not self.start_time:
			self.start_time = now_datetime()

		self.cans_damaged = cint(self.cans_damaged)
		not_delivered = cint(self.cans_loaded) - cint(self.cans_delivered)
		if self.cans_damaged > not_delivered:
			frappe.throw(
				f"Damaged cans ({self.cans_damaged}) cannot exceed the "
				f"{not_delivered} can(s) not yet delivered on this trip"
			)
		self.cans_remaining = not_delivered - self.cans_damaged

		if flt(self.end_km):
			if flt(self.end_km) < flt(self.start_km):
				frappe.throw("Ending KM cannot be less than Starting KM")
			self.distance_km = flt(self.end_km) - flt(self.start_km)
			if not self.end_time:
				self.end_time = now_datetime()
			self.status = "Completed"
			self.driver_credit = flt(self.route_price)
		else:
			self.distance_km = 0
			self.end_time = None
			self.status = "Active"
			self.driver_credit = 0

	def on_update(self):
		if self.status != "Completed" or not self.trip_route:
			return
		if frappe.db.exists("Driver Credit", {"trip": self.name}):
			return

		frappe.get_doc(
			{
				"doctype": "Driver Credit",
				"driver": self.driver,
				"trip": self.name,
				"credit_date": self.end_time.date(),
				"amount": self.driver_credit,
			}
		).insert(ignore_permissions=True)
