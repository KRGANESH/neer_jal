# Neer Jal

**Purified water can delivery, end to end.**
Customers, trips, sales, payroll, and reporting — all driven by a single **Trip**, delivered as an installable mobile PWA.

### Stack / Architecture

1. **Frappe Framework**: the backend, database, and admin/permission layer
2. **Vue 3 + FrappeUI** (Tailwind-based): a fully custom SPA frontend — not the standard Frappe Desk — served as an installable Progressive Web App
3. **wkhtmltopdf** (via Frappe's PDF utils): server-rendered HTML/CSS reports and payslips, exported as downloadable PDFs

### The Main Entity

The **Trip** is the primary entity of the delivery workflow. A trip is opened against a **Vehicle** and **Driver** (odometer + cans loaded), accumulates **Sales Entries** as deliveries happen along the route, and is closed out with a final odometer reading and a damaged/remaining-can count. Everything else — reports, LCR settlement, customer balances — is derived from trips.

### Features

Not an exhaustive list, just to give you an idea.

#### Sales & Delivery Tracking

Every delivery is recorded as a **Sales Entry** against a **Customer**, with automatic can-exchange accounting (cans given vs. cans returned) and five payment modes — Cash, UPI, Pending, LCR, and **Free** (for goodwill deliveries, forced to ₹0 and excluded from revenue). Customer can-balance and amount-due update automatically on every entry.

#### Customer Management

Customers get auto-generated 3-digit IDs, validated 10-digit phone numbers, and a per-customer SMS notification toggle.

#### Trips, Vehicles & Drivers

Trips guard against inconsistent odometer readings across successive trips on the same vehicle. Each closed trip can be exported as a landscape PDF **Trip Report** — vehicle, driver, sales person, timing, distance, and a full delivery breakdown by payment mode.

#### Employees & HR

A unified **Employee** doctype covers everyone on staff — plain employees, **Sales Person** logins (field delivery staff), and **Office Staff** logins (HR/admin). Full profile data is supported: personal details, address, education, employment status, and bank details.

- **Time Clock** — manual clock-in/clock-out, correctly handling shifts that cross midnight
- **Payroll** — run for any date range, paid to the exact minute (not rounded) against each employee's hourly wage, with a downloadable per-employee **Payslip** PDF

#### Reports & LCR

The **Delivery Report** breaks down sales by payment mode with per-mode subtotals, filterable by date range, customer, or sales person, and exportable as PDF. **LCR** (local cash receivable) tracks and settles cash a sales person personally collects in the field.

#### Roles

| Role | Access |
|---|---|
| **Sales Manager** | Full admin — customers, vehicles, drivers, employees, reports, settings |
| **Sales User** | Field delivery staff — record sales, view own trips |
| **Office Staff** | Time Clock + Payroll |
| **System Manager** | Superuser fallback |

#### PWA Behavior

Installed as a standalone app on mobile home screens. PDF downloads (reports, payslips) use the Web Share API with a blob-download fallback, since standalone PWA mode has no browser download UI. Login-required pages redirect guests straight to `/login`, and each role lands on its own home page post-login.

### Installation

\`\`\`bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/neerjal2026/neer_jal.git --branch main
bench --site <site-name> install-app neer_jal
\`\`\`

Roles (Sales Manager, Sales User, Office Staff) ship as fixtures and are created automatically on install.

