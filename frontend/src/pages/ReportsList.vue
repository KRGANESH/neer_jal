<template>
  <div class="mx-auto max-w-6xl p-4 sm:p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Reports</h1>
      <p class="text-sm text-gray-500">Filter deliveries and trip sheets by date, customer or driver</p>
    </div>

    <div class="boxed-fields mb-6 grid grid-cols-1 gap-4 rounded-lg border bg-white p-5 sm:grid-cols-2 lg:grid-cols-4">
      <FormControl type="date" label="From Date" v-model="filters.from_date" />
      <FormControl type="date" label="To Date" v-model="filters.to_date" />
      <FormControl
        type="select"
        label="Customer"
        :options="customerOptions"
        v-model="filters.customer"
      />
      <FormControl
        type="select"
        label="Driver"
        :options="driverOptions"
        v-model="filters.driver"
      />
      <div class="flex items-end gap-2 sm:col-span-2 lg:col-span-4">
        <Button theme="blue" variant="solid" :loading="report.loading || tripSheet.loading" @click="search">
          Search
        </Button>
        <Button theme="blue" variant="outline" :loading="downloading" @click="downloadPdf">
          Delivery PDF
        </Button>
        <Button theme="blue" variant="outline" :loading="tripSheetDownloading" @click="downloadTripSheetPdf">
          Trip Sheet PDF
        </Button>
      </div>
    </div>

    <div v-if="report.data" class="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Deliveries</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ report.data.entries.length }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Total Cans Given</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ report.data.totals.cans_given }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4">
        <p class="text-xs font-semibold uppercase text-gray-500">Total Amount</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ formatCurrency(report.data.totals.amount) }}</p>
      </div>
    </div>

    <div v-if="report.data" class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div v-for="mode in report.data.payment_modes" :key="mode" class="rounded-lg border bg-white p-4">
        <div class="flex items-center gap-2">
          <Badge :theme="paymentTheme(mode)" variant="subtle">{{ mode }}</Badge>
        </div>
        <p class="mt-1 text-xl font-semibold text-gray-900">
          {{ formatCurrency(report.data.totals.by_payment_mode[mode]) }}
        </p>
      </div>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[920px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Customer</th>
            <th class="px-4 py-3 font-medium">Driver</th>
            <th class="px-4 py-3 font-medium">Given</th>
            <th class="px-4 py-3 font-medium">Refill</th>
            <th
              v-for="mode in report.data?.payment_modes || []"
              :key="mode"
              class="px-4 py-3 font-medium text-right"
            >
              {{ mode }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in pagedEntries" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600">{{ row.sales_date }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.customer_name || row.customer }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.driver_name || row.driver }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.cans_given }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.cans_returned }}</td>
            <td
              v-for="mode in report.data.payment_modes"
              :key="mode"
              class="px-4 py-3 text-right text-gray-600"
            >
              {{ row.payment_mode === mode ? formatCurrency(row.amount) : '-' }}
            </td>
          </tr>
          <tr v-if="report.data && !report.data.entries.length">
            <td :colspan="5 + (report.data.payment_modes?.length || 0)" class="px-4 py-10 text-center text-gray-400">
              No deliveries found for these filters
            </td>
          </tr>
          <tr v-if="!report.data">
            <td colspan="5" class="px-4 py-10 text-center text-gray-400">
              Choose a date range and click Search
            </td>
          </tr>
        </tbody>
        <tfoot v-if="report.data && report.data.entries.length">
          <tr class="border-t bg-gray-50 font-semibold text-gray-900">
            <td class="px-4 py-3" colspan="3">Total ({{ report.data.entries.length }} deliveries)</td>
            <td class="px-4 py-3 text-right">{{ report.data.totals.cans_given }}</td>
            <td class="px-4 py-3 text-right">{{ report.data.totals.cans_returned }}</td>
            <td v-for="mode in report.data.payment_modes" :key="mode" class="px-4 py-3 text-right">
              {{ formatCurrency(report.data.totals.by_payment_mode[mode]) }}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="hasPreviousPage || hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!hasPreviousPage" @click="page--">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!hasNextPage" @click="page++">
        Next
      </Button>
    </div>

    <section class="mt-10">
      <div class="mb-4">
        <h2 class="text-xl font-semibold text-gray-900">Driver Trip Sheet</h2>
        <p class="text-sm text-gray-500">Trip routes, earned driver credit and customer deliveries for the selected period</p>
      </div>
      <div v-if="tripSheet.data" class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-5">
        <div class="rounded-lg border bg-white p-4"><p class="text-xs font-semibold uppercase text-gray-500">Trips</p><p class="mt-1 text-2xl font-semibold text-gray-900">{{ tripSheet.data.totals.trips }}</p></div>
        <div class="rounded-lg border bg-white p-4"><p class="text-xs font-semibold uppercase text-gray-500">Completed</p><p class="mt-1 text-2xl font-semibold text-gray-900">{{ tripSheet.data.totals.completed_trips }}</p></div>
        <div class="rounded-lg border bg-white p-4"><p class="text-xs font-semibold uppercase text-gray-500">Route Price Total</p><p class="mt-1 text-xl font-semibold text-gray-900">{{ formatCurrency(tripSheet.data.totals.route_price) }}</p></div>
        <div class="rounded-lg border bg-white p-4"><p class="text-xs font-semibold uppercase text-gray-500">Driver Credit</p><p class="mt-1 text-xl font-semibold text-gray-900">{{ formatCurrency(tripSheet.data.totals.driver_credit) }}</p></div>
        <div class="rounded-lg border bg-white p-4"><p class="text-xs font-semibold uppercase text-gray-500">Deliveries</p><p class="mt-1 text-2xl font-semibold text-gray-900">{{ tripSheet.data.totals.deliveries }}</p></div>
      </div>
      <div v-if="tripSheet.data" class="overflow-x-auto rounded-lg border bg-white">
        <table class="w-full min-w-[1040px] text-left text-sm">
          <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th class="px-4 py-3 font-medium">Date</th><th class="px-4 py-3 font-medium">Trip</th><th class="px-4 py-3 font-medium">Driver</th><th class="px-4 py-3 font-medium">Route</th>
              <th class="px-4 py-3 font-medium">Status</th><th class="px-4 py-3 font-medium">Route Price</th><th class="px-4 py-3 font-medium">Driver Credit</th>
              <th class="px-4 py-3 font-medium">Deliveries</th><th class="px-4 py-3 font-medium">Cans Given</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="trip in tripSheet.data.trips" :key="trip.name">
              <tr class="border-b">
                <td class="px-4 py-3 text-gray-600">{{ trip.start_time }}</td><td class="px-4 py-3 font-medium">{{ trip.name }}</td>
                <td class="px-4 py-3 text-gray-600">{{ trip.driver_name }}</td><td class="px-4 py-3 text-gray-600">{{ trip.route_name }}</td><td class="px-4 py-3">{{ trip.status }}</td>
                <td class="px-4 py-3">{{ formatCurrency(trip.route_price) }}</td><td class="px-4 py-3">{{ formatCurrency(trip.driver_credit) }}</td>
                <td class="px-4 py-3">{{ trip.deliveries.length }}</td><td class="px-4 py-3">{{ trip.cans_delivered || 0 }}</td>
              </tr>
              <tr v-for="delivery in trip.deliveries" :key="delivery.name" class="border-b bg-gray-50 text-xs">
                <td colspan="9" class="px-4 py-2 text-gray-600">
                  Delivery {{ delivery.sales_date }}: {{ delivery.customer_name || delivery.customer }}
                  · {{ delivery.cans_given }} cans given · {{ delivery.cans_returned }} refilled
                  · {{ formatCurrency(delivery.amount) }} ({{ delivery.payment_mode }})
                </td>
              </tr>
            </template>
            <tr v-if="!tripSheet.data.trips.length"><td colspan="9" class="px-4 py-10 text-center text-gray-400">No trips found for these filters</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="!tripSheet.data" class="rounded-lg border bg-white px-4 py-10 text-center text-gray-400">
        Search to load the driver trip sheet
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Button, FormControl, Badge, createResource, createListResource } from 'frappe-ui'
import { showError } from '@/utils/toast'
import { downloadFile } from '@/utils/download'

function today() {
  return new Date().toISOString().slice(0, 10)
}

function daysAgo(n) {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10)
}

const filters = reactive({
  from_date: daysAgo(30),
  to_date: today(),
  customer: '',
  driver: '',
})

const pageLength = 10
const page = ref(1)

const customers = createListResource({
  doctype: 'Customer',
  fields: ['name', 'customer_code', 'customer_name'],
  orderBy: 'customer_name asc',
  pageLength: 200,
  auto: true,
})

const drivers = createResource({
  url: 'neer_jal.api.users.list_sales_users',
  auto: true,
  params: { start: 0, page_length: 200 },
  initialData: [],
})

const customerOptions = computed(() => [
  { label: 'All Customers', value: '' },
  ...(customers.data || []).map((c) => ({ label: `${c.customer_code ? c.customer_code + ' - ' : ''}${c.customer_name}`, value: c.name })),
])

const driverOptions = computed(() => [
  { label: 'All Drivers', value: '' },
  ...(drivers.data || []).map((u) => ({ label: u.full_name, value: u.name })),
])

const report = createResource({
  url: 'neer_jal.api.reports.get_delivery_report',
})

const tripSheet = createResource({
  url: 'neer_jal.api.reports.get_driver_trip_sheet',
})

function search() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  page.value = 1
  report.submit(
    { ...filters },
    {
      onError(error) {
        showError(error, 'Could not load report')
      },
    },
  )
  tripSheet.submit(
    { from_date: filters.from_date, to_date: filters.to_date, driver: filters.driver },
    {
      onError(error) {
        showError(error, 'Could not load driver trip sheet')
      },
    },
  )
}

const pagedEntries = computed(() => {
  if (!report.data) return []
  const start = (page.value - 1) * pageLength
  return report.data.entries.slice(start, start + pageLength)
})

const hasPreviousPage = computed(() => page.value > 1)
const hasNextPage = computed(() => {
  if (!report.data) return false
  return page.value * pageLength < report.data.entries.length
})

const downloading = ref(false)

async function downloadPdf() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  downloading.value = true
  const params = new URLSearchParams({
    from_date: filters.from_date,
    to_date: filters.to_date,
  })
  if (filters.customer) params.set('customer', filters.customer)
  if (filters.driver) params.set('driver', filters.driver)
  const url = `/api/method/neer_jal.api.reports.download_delivery_report_pdf?${params.toString()}`
  const filename = `delivery-report-${filters.from_date}-to-${filters.to_date}.pdf`
  try {
    await downloadFile(url, filename)
  } catch {
    // downloadFile already surfaced a toast
  } finally {
    downloading.value = false
  }
}

const tripSheetDownloading = ref(false)

async function downloadTripSheetPdf() {
  if (!filters.from_date || !filters.to_date) {
    showError('Please choose both a from and to date')
    return
  }
  tripSheetDownloading.value = true
  const params = new URLSearchParams({ from_date: filters.from_date, to_date: filters.to_date })
  if (filters.driver) params.set('driver', filters.driver)
  try {
    await downloadFile(
      `/api/method/neer_jal.api.reports.download_driver_trip_sheet_pdf?${params.toString()}`,
      `driver-trip-sheet-${filters.from_date}-to-${filters.to_date}.pdf`,
    )
  } catch {
    // downloadFile already surfaced a toast
  } finally {
    tripSheetDownloading.value = false
  }
}

function paymentTheme(mode) {
  return { Cash: 'green', UPI: 'blue', Pending: 'red', LCR: 'orange', Free: 'gray' }[mode] || 'gray'
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
