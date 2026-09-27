import frappe

APP_ROLES = {"System Manager", "Sales Manager", "Sales User", "Office Staff"}
MANAGER_ROLES = {"System Manager", "Sales Manager"}
HR_ROLES = {"System Manager", "Sales Manager", "Office Staff"}


def has_app_permission():
	return bool(APP_ROLES & set(frappe.get_roles()))


@frappe.whitelist()
def get_my_roles():
	roles = frappe.get_roles()
	return {
		"roles": roles,
		"is_manager": bool(MANAGER_ROLES & set(roles)),
		"is_hr_manager": bool(HR_ROLES & set(roles)),
	}


def get_trip_permission_query(user):
	user = user or frappe.session.user
	if MANAGER_ROLES & set(frappe.get_roles(user)):
		return ""
	return f"`tabTrip`.driver = {frappe.db.escape(user)}"


def has_trip_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user
	if MANAGER_ROLES & set(frappe.get_roles(user)):
		return True
	return doc.driver == user
