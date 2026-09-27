<template>
  <Dialog v-model="show" :options="{ title: 'Close Trip', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl label="Vehicle" :model-value="trip?.vehicle" disabled />
        <FormControl label="Starting KM" :model-value="trip?.start_km" disabled />
        <FormControl label="Trip Route" :model-value="trip?.trip_route" disabled />
        <FormControl label="Driver Credit on Completion" :model-value="trip?.route_price || 0" disabled />
        <FormControl type="number" label="Ending KM (Odometer)" required v-model="endKm" />
        <FormControl label="Cans Loaded" :model-value="currentTrip?.cans_loaded" disabled />
        <FormControl
          label="Cans Delivered"
          :model-value="freshTrip.loading ? 'Loading...' : currentTrip?.cans_delivered || 0"
          disabled
        />
        <FormControl label="Cans Not Yet Delivered" :model-value="notDelivered" disabled />
        <FormControl
          type="number"
          label="Damaged Cans"
          v-model="damaged"
          :description="`Out of the ${notDelivered} not delivered, how many were damaged`"
        />
        <FormControl label="Cans Remaining (Good, Returned to Stock)" :model-value="finalRemaining" disabled />
      </div>
      <p v-if="distance !== null" class="mt-3 text-sm text-gray-500">
        Distance travelled: <span class="font-medium text-gray-900">{{ distance }} km</span>
      </p>
      <ErrorMessage class="mt-3 block" :message="closeTrip.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="closeTrip.loading" @click="submit">
        Close Trip
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  trip: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'closed'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const endKm = ref(0)
const damaged = ref(0)

const freshTrip = createResource({
  url: 'frappe.client.get',
})

watch(show, (value) => {
  if (value) {
    endKm.value = props.trip?.start_km || 0
    damaged.value = 0
    if (props.trip?.name) {
      freshTrip.submit({ doctype: 'Trip', name: props.trip.name })
    }
  }
})

// prefer the freshly-fetched trip (accurate cans_delivered even if a delivery
// happened after the parent's cached trip data was last loaded), falling back
// to the prop while the fresh fetch is in flight
const currentTrip = computed(() => freshTrip.data || props.trip)

const distance = computed(() => {
  if (!props.trip) return null
  const value = Number(endKm.value) - Number(props.trip.start_km)
  return Number.isFinite(value) ? value : null
})

const notDelivered = computed(() => {
  if (!currentTrip.value) return 0
  return Math.max(0, Number(currentTrip.value.cans_loaded || 0) - Number(currentTrip.value.cans_delivered || 0))
})

const finalRemaining = computed(() => Math.max(0, notDelivered.value - (Number(damaged.value) || 0)))

const closeTrip = createResource({
  url: 'frappe.client.set_value',
})

function submit() {
  if (Number(endKm.value) < Number(props.trip?.start_km)) {
    showError('Ending KM cannot be less than Starting KM')
    return
  }
  if (Number(damaged.value) > notDelivered.value) {
    showError(`Damaged cans cannot exceed the ${notDelivered.value} can(s) not yet delivered`)
    return
  }
  closeTrip.submit(
    {
      doctype: 'Trip',
      name: props.trip.name,
      fieldname: { end_km: endKm.value, cans_damaged: damaged.value },
    },
    {
      onSuccess() {
        showSuccess('Trip closed')
        show.value = false
        emit('closed')
      },
      onError(error) {
        showError(error, 'Could not close trip')
      },
    },
  )
}
</script>
