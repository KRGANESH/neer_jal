<template>
  <div class="mx-auto max-w-6xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Deliveries</h1>
        <p class="text-sm text-gray-500">Record cans given/returned and payments</p>
      </div>
      <Button
        theme="blue" variant="solid"
        class="w-full sm:w-auto"
        :disabled="!isManager && !hasActiveTrip"
        @click="showNewSale = true"
      >
        + New Delivery
      </Button>
    </div>

    <TripBanner v-model:has-trip="hasActiveTrip" @change="sales.reload()" />

    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
      <TabButtons v-model="activeTab" :buttons="tabs" @update:modelValue="onFilterChange" />
      <FormControl
        class="sm:ml-auto sm:w-64"
        type="text"
        placeholder="Search customer..."
        v-model="search"
        @update:modelValue="onSearch"
      />
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[880px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Customer</th>
            <th class="px-4 py-3 font-medium">Given</th>
            <th class="px-4 py-3 font-medium">Refill</th>
            <th class="px-4 py-3 font-medium">Rate</th>
            <th class="px-4 py-3 font-medium">Amount</th>
            <th class="px-4 py-3 font-medium">Payment</th>
            <th class="px-4 py-3 font-medium">Driver</th>
            <th class="px-4 py-3 font-medium">Trip</th>
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
            <td class="px-4 py-3 text-gray-600">{{ row.rate_per_can }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.amount }}</td>
            <td class="px-4 py-3">
              <Badge :theme="paymentTheme(row.payment_mode)" variant="subtle">{{ row.payment_mode }}</Badge>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ row.sales_person }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.trip || '-' }}</td>
          </tr>
          <tr v-if="!sales.list.loading && !sales.data?.length">
            <td colspan="9" class="px-4 py-10 text-center text-gray-400">No deliveries found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="sales.list.loading" class="mt-4 text-center text-sm text-gray-400">Loading...</div>

    <div class="mt-4 flex justify-center gap-2" v-if="sales.hasPreviousPage || sales.hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!sales.hasPreviousPage" @click="sales.previous()">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!sales.hasNextPage" @click="sales.next()">Next</Button>
    </div>

    <SalesFormDialog v-model="showNewSale" :list-resource="sales" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FormControl, Badge, TabButtons, createListResource } from 'frappe-ui'
import SalesFormDialog from '@/components/SalesFormDialog.vue'
import TripBanner from '@/components/TripBanner.vue'
import { isManager } from '@/utils/session'

const search = ref('')
const activeTab = ref('All')
const tabs = [
  { label: 'All' },
  { label: 'Cash' },
  { label: 'UPI' },
  { label: 'Pending' },
  { label: 'LCR' },
  { label: 'Free' },
]
const showNewSale = ref(false)
const hasActiveTrip = ref(true)

const sales = createListResource({
  doctype: 'Sales Entry',
  fields: [
    'name',
    'customer',
    'customer_name',
    'sales_date',
    'cans_given',
    'cans_returned',
    'rate_per_can',
    'amount',
    'payment_mode',
    'sales_person',
    'trip',
  ],
  orderBy: 'sales_date desc, creation desc',
  pageLength: 10,
  auto: true,
})

function paymentTheme(mode) {
  return { Cash: 'green', UPI: 'blue', Pending: 'red', LCR: 'orange', Free: 'gray' }[mode] || 'gray'
}

function buildFilters() {
  const filters = {}
  if (activeTab.value !== 'All') filters.payment_mode = activeTab.value
  if (search.value) filters.customer_name = ['like', `%${search.value}%`]
  return filters
}

function onFilterChange() {
  sales.update({ filters: buildFilters() })
  sales.reload()
}

let searchTimeout
function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(onFilterChange, 300)
}
</script>
