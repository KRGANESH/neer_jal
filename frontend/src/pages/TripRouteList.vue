<template>
  <div class="mx-auto max-w-3xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Trip Routes</h1>
        <p class="text-sm text-gray-500">Set the default driver credit for each route</p>
      </div>
      <Button theme="blue" variant="solid" class="w-full sm:w-auto" @click="openNew">+ New Route</Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[480px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Route</th>
            <th class="px-4 py-3 font-medium">Driver Credit</th>
            <th class="px-4 py-3 font-medium">Disabled</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in routes.data" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.route_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatCurrency(row.route_price) }}</td>
            <td class="px-4 py-3"><input type="checkbox" :checked="!!row.disabled" @change="toggleDisabled(row)" /></td>
            <td class="px-4 py-3 text-right"><Button theme="blue" variant="outline" @click="openEdit(row)">Edit</Button></td>
          </tr>
          <tr v-if="!routes.list.loading && !routes.data?.length">
            <td colspan="4" class="px-4 py-10 text-center text-gray-400">No trip routes added yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="routes.hasPreviousPage || routes.hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!routes.hasPreviousPage" @click="routes.previous()">Previous</Button>
      <Button theme="blue" variant="outline" :disabled="!routes.hasNextPage" @click="routes.next()">Next</Button>
    </div>

    <TripRouteFormDialog v-model="showDialog" :routes="routes" :route="editingRoute" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, createListResource } from 'frappe-ui'
import TripRouteFormDialog from '@/components/TripRouteFormDialog.vue'
import { showSuccess, showError } from '@/utils/toast'

const showDialog = ref(false)
const editingRoute = ref(null)
const routes = createListResource({
  doctype: 'Trip Route',
  fields: ['name', 'route_name', 'route_price', 'disabled'],
  orderBy: 'route_name asc',
  pageLength: 10,
  auto: true,
})

function openNew() {
  editingRoute.value = null
  showDialog.value = true
}

function openEdit(row) {
  editingRoute.value = row
  showDialog.value = true
}

function toggleDisabled(row) {
  routes.setValue.submit(
    { name: row.name, disabled: row.disabled ? 0 : 1 },
    {
      onSuccess() { showSuccess('Trip route updated') },
      onError(error) { showError(error, 'Could not update trip route') },
    },
  )
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
