import frappe
from frappe.utils import flt, getdate, now_datetime
from frappe.utils.pdf import get_pdf

from neer_jal.api.permission import MANAGER_ROLES


def _ensure_manager():
	if not (MANAGER_ROLES & set(frappe.get_roles())):
		frappe.throw("Not permitted", frappe.PermissionError)


def _get_payment_modes():
	options = frappe.get_meta("Sales Entry").get_field("payment_mode").options or ""
	return [mode for mode in options.split("\n") if mode]


def _get_filtered_entries(from_date, to_date, customer=None, driver=None):
	filters = {"sales_date": ["between", [getdate(from_date), getdate(to_date)]]}
	if customer:
		filters["customer"] = customer
	if driver:
		filters["sales_person"] = driver

	entries = frappe.get_all(
		"Sales Entry",
		filters=filters,
		fields=[
			"name",
			"sales_date",
			"customer",
			"customer_name",
			"sales_person as driver",
			"cans_given",
			"cans_returned",
			"rate_per_can",
			"amount",
			"payment_mode",
			"trip",
		],
		order_by="sales_date asc, creation asc",
	)

	driver_ids = {e.driver for e in entries if e.driver}
	names = _get_user_full_names(driver_ids)
	for e in entries:
		e.driver_name = names.get(e.driver, e.driver)

	return entries


def _get_user_full_names(user_ids):
	if not user_ids:
		return {}
	users = frappe.get_all("User", filters={"name": ["in", list(user_ids)]}, fields=["name", "full_name"])
	return {u.name: u.full_name for u in users}


def _get_customer_label(customer):
	return frappe.db.get_value("Customer", customer, "customer_name") or customer


def _get_totals(entries, payment_modes):
	by_payment_mode = {mode: 0 for mode in payment_modes}
	for e in entries:
		by_payment_mode[e.payment_mode] = by_payment_mode.get(e.payment_mode, 0) + flt(e.amount)

	return {
		"cans_given": sum(flt(e.cans_given) for e in entries),
		"cans_returned": sum(flt(e.cans_returned) for e in entries),
		"amount": sum(flt(e.amount) for e in entries),
		"by_payment_mode": by_payment_mode,
	}


@frappe.whitelist()
def get_delivery_report(from_date, to_date, customer=None, driver=None):
	_ensure_manager()
	entries = _get_filtered_entries(from_date, to_date, customer, driver)
	payment_modes = _get_payment_modes()
	totals = _get_totals(entries, payment_modes)
	return {"entries": entries, "totals": totals, "payment_modes": payment_modes}


def _build_report_html(from_date, to_date, customer, driver, entries, totals, payment_modes):
	customer_label = _get_customer_label(customer) if customer else "All Customers"
	driver_label = _get_user_full_names({driver}).get(driver, driver) if driver else "All Drivers"

	payment_headers = "".join(f'<th style="text-align:right">{mode}</th>' for mode in payment_modes)

	rows = "".join(
		f"""
		<tr>
			<td>{frappe.utils.format_date(e.sales_date)}</td>
			<td>{frappe.utils.escape_html(e.customer_name or e.customer)}</td>
			<td>{frappe.utils.escape_html(e.driver_name or e.driver)}</td>
			<td style="text-align:right">{flt(e.cans_given):g}</td>
			<td style="text-align:right">{flt(e.cans_returned):g}</td>
			{"".join(
				f'<td style="text-align:right">{flt(e.amount):.2f}</td>'
				if e.payment_mode == mode
				else '<td style="text-align:right">-</td>'
				for mode in payment_modes
			)}
		</tr>
		"""
		for e in entries
	)

	payment_totals = "".join(
		f'<td style="text-align:right">{totals["by_payment_mode"].get(mode, 0):.2f}</td>' for mode in payment_modes
	)

	col_count = 5 + len(payment_modes)

	return f"""
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
			h2 {{ margin-bottom: 0; }}
			.subtitle {{ color: #6b7280; margin-top: 4px; margin-bottom: 16px; }}
			table {{ width: 100%; border-collapse: collapse; }}
			th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; font-size: 11px; }}
			th {{ background-color: #eff6ff; text-align: left; }}
			.totals-row td {{ font-weight: bold; background-color: #f9fafb; }}
		</style>
	</head>
	<body>
		<h2>Neer Jal - Delivery Report</h2>
		<p class="subtitle">
			{frappe.utils.format_date(from_date)} to {frappe.utils.format_date(to_date)}
			&middot; Customer: {frappe.utils.escape_html(customer_label)}
			&middot; Driver: {frappe.utils.escape_html(driver_label)}
			&middot; Generated on {frappe.utils.format_datetime(now_datetime())}
		</p>
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Customer</th>
					<th>Driver</th>
					<th style="text-align:right">Given</th>
					<th style="text-align:right">Refill</th>
					{payment_headers}
				</tr>
			</thead>
			<tbody>
				{rows or f'<tr><td colspan="{col_count}" style="text-align:center">No deliveries found</td></tr>'}
				<tr class="totals-row">
					<td colspan="3">Total ({len(entries)} deliveries)</td>
					<td style="text-align:right">{totals['cans_given']:g}</td>
					<td style="text-align:right">{totals['cans_returned']:g}</td>
					{payment_totals}
				</tr>
				<tr class="totals-row">
					<td colspan="{col_count - 1}">Grand Total</td>
					<td style="text-align:right">{totals['amount']:.2f}</td>
				</tr>
			</tbody>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_delivery_report_pdf(from_date, to_date, customer=None, driver=None):
	_ensure_manager()
	entries = _get_filtered_entries(from_date, to_date, customer, driver)
	payment_modes = _get_payment_modes()
	totals = _get_totals(entries, payment_modes)
	html = _build_report_html(from_date, to_date, customer, driver, entries, totals, payment_modes)

	frappe.local.response.filename = (
		f"delivery-report-{getdate(from_date)}-to-{getdate(to_date)}.pdf"
	)
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"


def _ensure_trip_access(trip_doc):
	if MANAGER_ROLES & set(frappe.get_roles()):
		return
	if trip_doc.driver == frappe.session.user:
		return
	frappe.throw("Not permitted", frappe.PermissionError)


def _get_trip_entries(trip):
	entries = frappe.get_all(
		"Sales Entry",
		filters={"trip": trip},
		fields=[
			"name",
			"sales_date",
			"customer",
			"customer_name",
			"cans_given",
			"cans_returned",
			"amount",
			"payment_mode",
		],
		order_by="sales_date asc, creation asc",
	)
	return entries


def _build_trip_report_html(trip_doc, driver_name, entries, totals, payment_modes):
	payment_headers = "".join(f'<th style="text-align:right">{mode}</th>' for mode in payment_modes)

	rows = "".join(
		f"""
		<tr>
			<td>{frappe.utils.format_date(e.sales_date)}</td>
			<td>{frappe.utils.escape_html(e.customer_name or e.customer)}</td>
			<td style="text-align:right">{flt(e.cans_given):g}</td>
			<td style="text-align:right">{flt(e.cans_returned):g}</td>
			{"".join(
				f'<td style="text-align:right">{flt(e.amount):.2f}</td>'
				if e.payment_mode == mode
				else '<td style="text-align:right">-</td>'
				for mode in payment_modes
			)}
		</tr>
		"""
		for e in entries
	)

	payment_totals = "".join(
		f'<td style="text-align:right">{totals["by_payment_mode"].get(mode, 0):.2f}</td>' for mode in payment_modes
	)

	col_count = 4 + len(payment_modes)

	def detail(label, value):
		return f'<div class="detail"><span class="label">{label}</span><span class="value">{value}</span></div>'

	details = "".join(
		[
			detail("Vehicle", trip_doc.vehicle or "-"),
			detail("Driver", frappe.utils.escape_html(driver_name or trip_doc.driver or "-")),
			detail("Trip Route", frappe.utils.escape_html(getattr(trip_doc, "trip_route_name", None) or trip_doc.trip_route or "-")),
			detail("Route Price", f"{flt(trip_doc.route_price):.2f}"),
			detail("Driver Credit", f"{flt(trip_doc.driver_credit):.2f}"),
			detail("Status", trip_doc.status),
			detail("Start Time", trip_doc.start_time or "-"),
			detail("End Time", trip_doc.end_time or "-"),
			detail("Start KM", trip_doc.start_km if trip_doc.start_km is not None else "-"),
			detail("End KM", trip_doc.end_km or "-"),
			detail("Distance", f"{trip_doc.distance_km} km" if trip_doc.distance_km else "-"),
			detail("Cans Loaded", trip_doc.cans_loaded or 0),
			detail("Cans Delivered", trip_doc.cans_delivered or 0),
			detail("Cans Damaged", trip_doc.cans_damaged or 0),
			detail(
				"Cans Remaining (Good)",
				trip_doc.cans_remaining if trip_doc.status == "Completed" else "-",
			),
		]
	)

	return f"""
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
			h2 {{ margin-bottom: 0; }}
			.subtitle {{ color: #6b7280; margin-top: 4px; margin-bottom: 16px; }}
			/* wkhtmltopdf's flexbox support is unreliable, so this uses a plain
			   float-based grid instead - it renders correctly in PDF output. */
			.details {{ overflow: hidden; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb; }}
			.detail {{ float: left; width: 25%; box-sizing: border-box; padding-right: 12px; margin-bottom: 12px; }}
			.detail .label {{ display: block; font-size: 10px; text-transform: uppercase; color: #6b7280; margin-bottom: 3px; }}
			.detail .value {{ display: block; font-size: 13px; font-weight: bold; }}
			table {{ width: 100%; border-collapse: collapse; }}
			th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; font-size: 11px; }}
			th {{ background-color: #eff6ff; text-align: left; }}
			.totals-row td {{ font-weight: bold; background-color: #f9fafb; }}
		</style>
	</head>
	<body>
		<h2>Neer Jal - Trip Report</h2>
		<p class="subtitle">
			{trip_doc.name} &middot; Generated on {frappe.utils.format_datetime(now_datetime())}
		</p>
		<div class="details">{details}</div>
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Customer</th>
					<th style="text-align:right">Given</th>
					<th style="text-align:right">Refill</th>
					{payment_headers}
				</tr>
			</thead>
			<tbody>
				{rows or f'<tr><td colspan="{col_count}" style="text-align:center">No deliveries recorded on this trip</td></tr>'}
				<tr class="totals-row">
					<td colspan="2">Total ({len(entries)} deliveries)</td>
					<td style="text-align:right">{totals['cans_given']:g}</td>
					<td style="text-align:right">{totals['cans_returned']:g}</td>
					{payment_totals}
				</tr>
				<tr class="totals-row">
					<td colspan="{col_count - 1}">Grand Total</td>
					<td style="text-align:right">{totals['amount']:.2f}</td>
				</tr>
			</tbody>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_trip_report_pdf(trip):
	trip_doc = frappe.get_doc("Trip", trip)
	_ensure_trip_access(trip_doc)
	trip_doc.trip_route_name = (
		frappe.db.get_value("Trip Route", trip_doc.trip_route, "route_name") if trip_doc.trip_route else None
	)

	entries = _get_trip_entries(trip)
	payment_modes = _get_payment_modes()
	totals = _get_totals(entries, payment_modes)

	driver_name = _get_user_full_names({trip_doc.driver}).get(trip_doc.driver) if trip_doc.driver else None

	html = _build_trip_report_html(trip_doc, driver_name, entries, totals, payment_modes)

	frappe.local.response.filename = f"trip-report-{trip_doc.name}.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"


def _get_driver_trip_sheet(from_date, to_date, driver=None):
	filters = {
		"start_time": [
			"between",
			[f"{getdate(from_date)} 00:00:00", f"{getdate(to_date)} 23:59:59"],
		]
	}
	if driver:
		filters["driver"] = driver

	trips = frappe.get_all(
		"Trip",
		filters=filters,
		fields=[
			"name", "driver", "trip_route", "route_price", "driver_credit", "status",
			"start_time", "end_time", "vehicle", "start_km", "end_km", "distance_km",
			"cans_loaded", "cans_delivered", "cans_damaged", "cans_remaining",
		],
		order_by="start_time asc",
	)

	trip_names = [trip.name for trip in trips]
	route_ids = {trip.trip_route for trip in trips if trip.trip_route}
	route_names = {
		row.name: row.route_name
		for row in frappe.get_all(
			"Trip Route", filters={"name": ["in", list(route_ids)]}, fields=["name", "route_name"]
		)
	}
	driver_ids = {trip.driver for trip in trips if trip.driver}
	driver_names = _get_user_full_names(driver_ids)
	driver_credits = frappe.get_all(
		"Driver Credit",
		filters={"trip": ["in", trip_names]} if trip_names else {"name": "__none__"},
		fields=["trip", "amount"],
	)
	credit_by_trip = {credit.trip: flt(credit.amount) for credit in driver_credits}
	deliveries = frappe.get_all(
		"Sales Entry",
		filters={"trip": ["in", trip_names]} if trip_names else {"name": "__none__"},
		fields=[
			"name", "trip", "sales_date", "customer", "customer_name", "cans_given",
			"cans_returned", "amount", "payment_mode",
		],
		order_by="sales_date asc, creation asc",
	)
	deliveries_by_trip = {}
	for delivery in deliveries:
		deliveries_by_trip.setdefault(delivery.trip, []).append(delivery)

	for trip in trips:
		trip.driver_name = driver_names.get(trip.driver, trip.driver)
		trip.route_name = route_names.get(trip.trip_route, trip.trip_route or "-")
		trip.driver_credit = credit_by_trip.get(trip.name, 0)
		trip.deliveries = deliveries_by_trip.get(trip.name, [])

	return {
		"trips": trips,
		"totals": {
			"trips": len(trips),
			"completed_trips": sum(1 for trip in trips if trip.status == "Completed"),
			"route_price": sum(flt(trip.route_price) for trip in trips),
			"driver_credit": sum(flt(trip.driver_credit) for trip in trips),
			"deliveries": len(deliveries),
			"cans_delivered": sum(flt(delivery.cans_given) for delivery in deliveries),
		},
	}


@frappe.whitelist()
def get_driver_trip_sheet(from_date, to_date, driver=None):
	_ensure_manager()
	return _get_driver_trip_sheet(from_date, to_date, driver)


def _build_driver_trip_sheet_html(from_date, to_date, data, driver=None):
	driver_label = _get_user_full_names({driver}).get(driver, driver) if driver else "All Drivers"

	rows = []
	for trip in data["trips"]:
		for delivery in trip.deliveries or [None]:
			if delivery:
				rows.append(
					f"""
					<tr>
						<td>{frappe.utils.format_date(trip.start_time)}</td>
						<td>{frappe.utils.escape_html(trip.name)}</td>
						<td>{frappe.utils.escape_html(trip.driver_name)}</td>
						<td>{frappe.utils.escape_html(trip.route_name)}</td>
						<td>{frappe.utils.escape_html(trip.status)}</td>
						<td style="text-align:right">{flt(trip.route_price):.2f}</td>
						<td style="text-align:right">{flt(trip.driver_credit):.2f}</td>
						<td>{frappe.utils.format_date(delivery.sales_date)} - {frappe.utils.escape_html(delivery.customer_name or delivery.customer)}</td>
						<td style="text-align:right">{flt(delivery.cans_given):g}</td>
						<td style="text-align:right">{flt(delivery.cans_returned):g}</td>
						<td style="text-align:right">{flt(delivery.amount):.2f} ({frappe.utils.escape_html(delivery.payment_mode)})</td>
					</tr>
					"""
				)
			else:
				rows.append(
					f"""
					<tr>
						<td>{frappe.utils.format_date(trip.start_time)}</td>
						<td>{frappe.utils.escape_html(trip.name)}</td>
						<td>{frappe.utils.escape_html(trip.driver_name)}</td>
						<td>{frappe.utils.escape_html(trip.route_name)}</td>
						<td>{frappe.utils.escape_html(trip.status)}</td>
						<td style="text-align:right">{flt(trip.route_price):.2f}</td>
						<td style="text-align:right">{flt(trip.driver_credit):.2f}</td>
						<td colspan="4">No deliveries</td>
					</tr>
					"""
				)

	totals = data["totals"]
	return f"""
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
		h2 {{ margin-bottom: 0; }}
		.subtitle {{ color: #6b7280; margin: 4px 0 16px; }}
		table {{ width: 100%; border-collapse: collapse; }}
		th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; font-size: 10px; }}
		th {{ background-color: #eff6ff; text-align: left; }}
		.total td {{ font-weight: bold; background-color: #f9fafb; }}
		</style>
	</head>
	<body>
		<h2>Neer Jal - Driver Trip Sheet</h2>
		<p class="subtitle">{frappe.utils.format_date(from_date)} to {frappe.utils.format_date(to_date)} &middot; {frappe.utils.escape_html(driver_label)}</p>
		<table>
			<thead><tr><th>Date</th><th>Trip</th><th>Driver</th><th>Route</th><th>Status</th><th>Route Price</th><th>Driver Credit</th><th>Delivery</th><th>Given</th><th>Refill</th><th>Amount / Mode</th></tr></thead>
			<tbody>
				{"".join(rows) or '<tr><td colspan="11" style="text-align:center">No trips found</td></tr>'}
				<tr class="total"><td colspan="5">Totals ({totals['trips']} trips, {totals['deliveries']} deliveries)</td><td style="text-align:right">{totals['route_price']:.2f}</td><td style="text-align:right">{totals['driver_credit']:.2f}</td><td></td><td colspan="3">Cans delivered: {totals['cans_delivered']:g}</td></tr>
			</tbody>
		</table>
	</body>
	</html>
	"""


@frappe.whitelist()
def download_driver_trip_sheet_pdf(from_date, to_date, driver=None):
	_ensure_manager()
	data = _get_driver_trip_sheet(from_date, to_date, driver)
	html = _build_driver_trip_sheet_html(from_date, to_date, data, driver)
	frappe.local.response.filename = f"driver-trip-sheet-{getdate(from_date)}-to-{getdate(to_date)}.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape"})
	frappe.local.response.type = "pdf"
