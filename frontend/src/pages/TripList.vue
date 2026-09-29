<template>
  <div class="mx-auto max-w-5xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Trips</h1>
        <p class="text-sm text-gray-500">
          {{ isManager ? 'All driver trips' : 'Your trips' }}
        </p>
      </div>
    </div>

    <div class="boxed-fields mb-4 grid grid-cols-1 gap-4 rounded-lg border bg-white p-4 sm:grid-cols-2 lg:grid-cols-3">
      <FormControl type="date" label="Date" v-model="selectedDate" @update:modelValue="onFilterChange" />
      <FormControl
        v-if="isManager"
        type="select"
        label="Driver"
        :options="driverOptions"
        v-model="selectedDriver"
        @update:modelValue="onFilterChange"
      />
      <div class="flex items-end">
        <TabButtons v-model="activeTab" :buttons="tabs" @update:modelValue="onFilterChange" />
      </div>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[820px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Started</th>
            <th class="px-4 py-3 font-medium">Vehicle</th>
            <th class="px-4 py-3 font-medium">Driver</th>
            <th class="px-4 py-3 font-medium">Route</th>
            <th class="px-4 py-3 font-medium">Start / End KM</th>
            <th class="px-4 py-3 font-medium">Distance</th>
            <th class="px-4 py-3 font-medium">Cans (Loaded/Delivered)</th>
            <th class="px-4 py-3 font-medium">Driver Credit</th>
            <th class="px-4 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in trips.data"
            :key="row.name"
            class="cursor-pointer border-b last:border-0 hover:bg-gray-50"
            @click="$router.push(`/trips/${row.name}`)"
          >
            <td class="px-4 py-3 text-gray-600">{{ row.start_time }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.vehicle }}</td>
            <td class="px-4 py-3 text-gray-600">{{ driverLabel(row.driver) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ routeLabel(row.trip_route) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.start_km }} / {{ row.end_km || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.distance_km || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.cans_loaded }} / {{ row.cans_delivered || 0 }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.driver_credit || 0 }}</td>
            <td class="px-4 py-3">
              <Badge :theme="row.status === 'Active' ? 'orange' : 'green'" variant="subtle">
                {{ row.status }}
              </Badge>
            </td>
          </tr>
          <tr v-if="!trips.list.loading && !trips.data?.length">
            <td colspan="9" class="px-4 py-10 text-center text-gray-400">No trips found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="trips.list.loading" class="mt-4 text-center text-sm text-gray-400">Loading...</div>

    <div class="mt-4 flex justify-center gap-2" v-if="trips.hasPreviousPage || trips.hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!trips.hasPreviousPage" @click="trips.previous()">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!trips.hasNextPage" @click="trips.next()">Next</Button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Button, Badge, FormControl, TabButtons, createListResource, createResource } from 'frappe-ui'
import { isManager } from '@/utils/session'

function today() {
  return new Date().toISOString().slice(0, 10)
}

const activeTab = ref('All')
const tabs = [{ label: 'All' }, { label: 'Active' }, { label: 'Completed' }]
const selectedDate = ref(today())
const selectedDriver = ref('')

const drivers = createResource({
  url: 'neer_jal.api.users.list_sales_users',
  auto: false,
  params: { start: 0, page_length: 200 },
  initialData: [],
})

watch(isManager, (value) => {
  if (value) drivers.reload()
}, { immediate: true })

const routes = createListResource({
  doctype: 'Trip Route',
  fields: ['name', 'route_name'],
  pageLength: 200,
  auto: true,
})

const driverOptions = computed(() => [
  { label: 'All Drivers', value: '' },
  ...(drivers.data || []).map((u) => ({ label: u.full_name, value: u.name })),
])

function buildFilters() {
  const filters = {}
  if (activeTab.value !== 'All') filters.status = activeTab.value
  if (selectedDate.value) {
    filters.start_time = ['between', [`${selectedDate.value} 00:00:00`, `${selectedDate.value} 23:59:59`]]
  }
  if (selectedDriver.value) filters.driver = selectedDriver.value
  return filters
}

const trips = createListResource({
  doctype: 'Trip',
  fields: [
    'name',
    'vehicle',
    'driver',
    'trip_route',
    'route_price',
    'driver_credit',
    'status',
    'start_km',
    'end_km',
    'distance_km',
    'start_time',
    'cans_loaded',
    'cans_delivered',
  ],
  orderBy: 'creation desc',
  pageLength: 10,
  filters: buildFilters(),
  auto: true,
})

function driverLabel(driver) {
  return drivers.data?.find((user) => user.name === driver)?.full_name || driver
}

function routeLabel(route) {
  return routes.data?.find((item) => item.name === route)?.route_name || route || '-'
}

function onFilterChange() {
  trips.update({ filters: buildFilters() })
  trips.reload()
}
</script>
