app_name = "neer_jal"
app_title = "Neer Jal"
app_publisher = "Neer Jal"
app_description = "Neer Jal"
app_email = "support@neerjal.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Fixtures
# --------
# Ship the roles this app's permissions depend on, so they exist on any site
# this app is installed on (they are not guaranteed to exist on a fresh site).
fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Sales Manager", "Sales User", "Office Staff"]]]},
]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "neer_jal",
		"logo": "/neer_jal/favicon.svg",
		"title": "Neer Jal",
		"route": "/neer_jal",
		"has_permission": "neer_jal.api.permission.has_app_permission",
	}
]

# Website Route Rules
# --------------------
# Only the known SPA client-side routes are rewritten to the app shell (neer_jal.html).
# Everything else under /neer_jal/ (JS/CSS bundles, manifest.webmanifest, sw.js, icons)
# is a real static file under www/neer_jal/ and is left alone so it's served as-is -
# this keeps the service worker's scope covering the whole /neer_jal/ path.
website_route_rules = [
	{"from_route": "/neer_jal/customers/<path:customer_id>", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/customers", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/sales", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/vehicles", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/trip-routes", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/employees", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/time-clock", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/time-clock/<path:employee>", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/payroll", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/salary-advances", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/trips/<path:trip_id>", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/trips", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/reports", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/lcr", "to_route": "neer_jal"},
	{"from_route": "/neer_jal/settings", "to_route": "neer_jal"},
	{"from_route": "/neer_jal", "to_route": "neer_jal"},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/neer_jal/css/neer_jal.css"
# app_include_js = "/assets/neer_jal/js/neer_jal.js"

# include js, css files in header of web template
# web_include_css = "/assets/neer_jal/css/neer_jal.css"
# web_include_js = "/assets/neer_jal/js/neer_jal.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "neer_jal/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "neer_jal/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Sales Manager": "neer_jal",
	"Sales User": "neer_jal",
	"Office Staff": "neer_jal",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "neer_jal.utils.jinja_methods",
# 	"filters": "neer_jal.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "neer_jal.install.before_install"
# after_install = "neer_jal.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "neer_jal.uninstall.before_uninstall"
# after_uninstall = "neer_jal.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "neer_jal.utils.before_app_install"
# after_app_install = "neer_jal.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "neer_jal.utils.before_app_uninstall"
# after_app_uninstall = "neer_jal.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "neer_jal.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Trip": "neer_jal.api.permission.get_trip_permission_query",
}

has_permission = {
	"Trip": "neer_jal.api.permission.has_trip_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"neer_jal.tasks.all"
# 	],
# 	"daily": [
# 		"neer_jal.tasks.daily"
# 	],
# 	"hourly": [
# 		"neer_jal.tasks.hourly"
# 	],
# 	"weekly": [
# 		"neer_jal.tasks.weekly"
# 	],
# 	"monthly": [
# 		"neer_jal.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "neer_jal.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "neer_jal.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "neer_jal.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["neer_jal.utils.before_request"]
# after_request = ["neer_jal.utils.after_request"]

# Job Events
# ----------
# before_job = ["neer_jal.utils.before_job"]
# after_job = ["neer_jal.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"neer_jal.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

