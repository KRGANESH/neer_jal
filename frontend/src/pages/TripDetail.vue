<template>
  <div class="mx-auto max-w-5xl p-4 sm:p-6" v-if="trip.doc">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <router-link to="/trips" class="text-sm text-gray-500 hover:underline">
          &larr; Trips
        </router-link>
        <h1 class="mt-1 text-2xl font-semibold text-gray-900">{{ trip.doc.name }}</h1>
        <p class="text-sm text-gray-500">Started {{ trip.doc.start_time }}</p>
      </div>
      <div class="flex gap-2">
        <Button theme="blue" variant="outline" :loading="downloading" @click="downloadPdf">
          Export PDF
        </Button>
        <Button v-if="trip.doc.status === 'Active'" theme="blue" variant="solid" @click="showClose = true">
          Close Trip
        </Button>
      </div>
    </div>

    <div class="mb-8 rounded-lg border bg-white p-5">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase text-gray-500">Trip Details</h2>
        <Badge :theme="trip.doc.status === 'Active' ? 'orange' : 'green'" variant="subtle">
          {{ trip.doc.status }}
        </Badge>
      </div>
      <div class="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
        <div><span class="text-gray-500">Vehicle:</span> <span class="text-gray-900">{{ trip.doc.vehicle }}</span></div>
        <div><span class="text-gray-500">Driver:</span> <span class="text-gray-900">{{ trip.doc.driver }}</span></div>
        <div><span class="text-gray-500">Trip Route:</span> <span class="text-gray-900">{{ routeLabel(trip.doc.trip_route) }}</span></div>
        <div><span class="text-gray-500">Route Price:</span> <span class="text-gray-900">{{ formatCurrency(trip.doc.route_price) }}</span></div>
        <div><span class="text-gray-500">Driver Credit:</span> <span class="text-gray-900">{{ formatCurrency(trip.doc.driver_credit) }}</span></div>
        <div><span class="text-gray-500">Starting KM:</span> <span class="text-gray-900">{{ trip.doc.start_km }}</span></div>
        <div><span class="text-gray-500">Ending KM:</span> <span class="text-gray-900">{{ trip.doc.end_km || '-' }}</span></div>
        <div><span class="text-gray-500">Distance:</span> <span class="text-gray-900">{{ trip.doc.distance_km || '-' }} km</span></div>
        <div><span class="text-gray-500">Start Time:</span> <span class="text-gray-900">{{ trip.doc.start_time }}</span></div>
        <div><span class="text-gray-500">End Time:</span> <span class="text-gray-900">{{ trip.doc.end_time || '-' }}</span></div>
        <div><span class="text-gray-500">Cans Loaded:</span> <span class="text-gray-900">{{ trip.doc.cans_loaded }}</span></div>
        <div><span class="text-gray-500">Cans Delivered:</span> <span class="text-gray-900">{{ trip.doc.cans_delivered || 0 }}</span></div>
        <div><span class="text-gray-500">Cans Damaged:</span> <span class="text-gray-900">{{ trip.doc.cans_damaged || 0 }}</span></div>
        <div><span class="text-gray-500">Cans Remaining (Good):</span> <span class="text-gray-900">{{ trip.doc.status === 'Completed' ? trip.doc.cans_remaining : '-' }}</span></div>
        <div class="sm:col-span-2" v-if="trip.doc.notes">
          <span class="text-gray-500">Notes:</span> <span class="text-gray-900">{{ trip.doc.notes }}</span>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-white">
      <div class="border-b p-5">
        <h2 class="text-sm font-semibold uppercase text-gray-500">Deliveries</h2>
        <p class="text-xs text-gray-400">{{ sales.data?.length || 0 }} delivery(ies) on this trip</p>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[640px] text-left text-sm">
          <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th class="px-4 py-3 font-medium">Date</th>
              <th class="px-4 py-3 font-medium">Customer</th>
              <th class="px-4 py-3 font-medium">Given</th>
              <th class="px-4 py-3 font-medium">Refill</th>
              <th class="px-4 py-3 font-medium">Amount</th>
              <th class="px-4 py-3 font-medium">Payment</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in sales.data"
              :key="row.name"
              class="cursor-pointer border-b last:border-0 hover:bg-gray-50"
              @click="$router.push(`/customers/${row.customer}`)"
            >
              <td class="px-4 py-3 text-gray-600">{{ row.sales_date }}</td>
              <td class="px-4 py-3 font-medium text-gray-900">{{ row.customer_name || row.customer }}</td>
              <td class="px-4 py-3 text-gray-600">{{ row.cans_given }}</td>
              <td class="px-4 py-3 text-gray-600">{{ row.cans_returned }}</td>
              <td class="px-4 py-3 text-gray-600">{{ row.amount }}</td>
              <td class="px-4 py-3">
                <Badge :theme="paymentTheme(row.payment_mode)" variant="subtle">{{ row.payment_mode }}</Badge>
              </td>
            </tr>
            <tr v-if="!sales.list.loading && !sales.data?.length">
              <td colspan="6" class="px-4 py-10 text-center text-gray-400">
                No deliveries recorded on this trip yet
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="flex justify-center gap-2 border-t p-4" v-if="sales.hasPreviousPage || sales.hasNextPage">
        <Button theme="blue" variant="outline" :disabled="!sales.hasPreviousPage" @click="sales.previous()">
          Previous
        </Button>
        <Button theme="blue" variant="outline" :disabled="!sales.hasNextPage" @click="sales.next()">
          Next
        </Button>
      </div>
    </div>

    <TripCloseDialog v-model="showClose" :trip="trip.doc" @closed="onClosed" />
  </div>
  <div v-else class="p-6 text-gray-400">Loading...</div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, Badge, createDocumentResource, createListResource } from 'frappe-ui'
import TripCloseDialog from '@/components/TripCloseDialog.vue'
import { downloadFile } from '@/utils/download'
import { showError } from '@/utils/toast'

const props = defineProps({
  tripId: { type: String, required: true },
})

const showClose = ref(false)

const trip = createDocumentResource({
  doctype: 'Trip',
  name: props.tripId,
})

const sales = createListResource({
  doctype: 'Sales Entry',
  fields: [
    'name',
    'customer',
    'customer_name',
    'sales_date',
    'cans_given',
    'cans_returned',
    'amount',
    'payment_mode',
  ],
  filters: { trip: props.tripId },
  orderBy: 'sales_date desc, creation desc',
  pageLength: 10,
  auto: true,
})

const routes = createListResource({
  doctype: 'Trip Route',
  fields: ['name', 'route_name'],
  pageLength: 200,
  auto: true,
})

function routeLabel(route) {
  return routes.data?.find((item) => item.name === route)?.route_name || route || '-'
}

function paymentTheme(mode) {
  return { Cash: 'green', UPI: 'blue', Pending: 'red', LCR: 'orange', Free: 'gray' }[mode] || 'gray'
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function onClosed() {
  trip.reload()
}

const downloading = ref(false)

async function downloadPdf() {
  downloading.value = true
  const url = `/api/method/neer_jal.api.reports.download_trip_report_pdf?trip=${props.tripId}`
  const filename = `trip-report-${props.tripId}.pdf`
  try {
    await downloadFile(url, filename)
  } catch (error) {
    showError(error, 'Could not download trip report')
  } finally {
    downloading.value = false
  }
}
</script>
