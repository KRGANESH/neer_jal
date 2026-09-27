# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class TripRoute(Document):
	def validate(self):
		if flt(self.route_price) < 0:
			frappe.throw("Driver trip price cannot be negative")
