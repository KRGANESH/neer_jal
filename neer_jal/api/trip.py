import frappe


@frappe.whitelist()
def get_active_trip():
	name = frappe.db.get_value(
		"Trip", {"driver": frappe.session.user, "status": "Active"}, "name"
	)
	if not name:
		return None
	trip = frappe.get_doc("Trip", name).as_dict()
	trip["driver_name"] = frappe.db.get_value("User", trip.driver, "full_name") or trip.driver
	trip["trip_route_name"] = (
		frappe.db.get_value("Trip Route", trip.trip_route, "route_name") if trip.trip_route else None
	)
	return trip
