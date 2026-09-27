<template>
  <Dialog v-model="show" :options="{ title: 'Start Trip', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl
          type="select"
          label="Vehicle"
          required
          :options="vehicleOptions"
          v-model="form.vehicle"
        />
        <FormControl
          type="select"
          label="Trip Route"
          required
          :options="routeOptions"
          v-model="form.trip_route"
        />
        <FormControl type="number" label="Starting KM (Odometer)" required v-model="form.start_km" />
        <FormControl
          type="number"
          label="Cans Loaded for Trip"
          required
          v-model="form.cans_loaded"
          description="Total full cans being taken on this trip"
        />
      </div>
      <ErrorMessage class="mt-3 block" :message="startTrip.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="startTrip.loading" @click="submit">
        Start Trip
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createListResource, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'started'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const vehicles = createListResource({
  doctype: 'Vehicle',
  fields: ['name', 'vehicle_number', 'model'],
  filters: { disabled: 0 },
  orderBy: 'vehicle_number asc',
  pageLength: 100,
  auto: true,
})

const routes = createListResource({
  doctype: 'Trip Route',
  fields: ['name', 'route_name', 'route_price'],
  filters: { disabled: 0 },
  orderBy: 'route_name asc',
  pageLength: 100,
  auto: true,
})

const vehicleOptions = computed(() =>
  (vehicles.data || []).map((v) => ({
    label: v.model ? `${v.vehicle_number} (${v.model})` : v.vehicle_number,
    value: v.name,
  })),
)

const routeOptions = computed(() =>
  (routes.data || []).map((route) => ({
    label: `${route.route_name} (${Number(route.route_price || 0).toFixed(2)})`,
    value: route.name,
  })),
)

function emptyForm() {
  return { vehicle: '', trip_route: '', start_km: 0, cans_loaded: 0 }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

const startTrip = createResource({
  url: 'frappe.client.insert',
})

function submit() {
  if (!form.vehicle || !form.trip_route) {
    showError('Please select a vehicle and trip route')
    return
  }
  if (!form.cans_loaded || Number(form.cans_loaded) <= 0) {
    showError('Please enter how many cans are being loaded for this trip')
    return
  }
  startTrip.submit(
    {
      doc: {
        doctype: 'Trip',
        vehicle: form.vehicle,
        trip_route: form.trip_route,
        start_km: form.start_km,
        cans_loaded: form.cans_loaded,
      },
    },
    {
      onSuccess(doc) {
        showSuccess('Trip started')
        show.value = false
        emit('started', doc)
      },
      onError(error) {
        showError(error, 'Could not start trip')
      },
    },
  )
}
</script>
