<template>
  <div class="mb-4 rounded-lg border bg-white p-4">
    <div v-if="activeTrip.data" class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm">
        <span class="font-medium text-gray-900">Trip in progress</span>
        <span class="text-gray-500">Vehicle: <span class="text-gray-900">{{ activeTrip.data.vehicle }}</span></span>
        <span class="text-gray-500">Driver: <span class="text-gray-900">{{ activeTrip.data.driver_name }}</span></span>
        <span class="text-gray-500">Route: <span class="text-gray-900">{{ activeTrip.data.trip_route_name }}</span></span>
        <span class="text-gray-500">Route Price: <span class="text-gray-900">{{ activeTrip.data.route_price }}</span></span>
        <span class="text-gray-500">Start KM: <span class="text-gray-900">{{ activeTrip.data.start_km }}</span></span>
      </div>
      <Button theme="blue" variant="outline" @click="showClose = true">Close Trip</Button>
    </div>
    <div v-else class="flex flex-wrap items-center justify-between gap-3">
      <p class="text-sm text-gray-500">
        You don't have an active trip.
        <span v-if="canStartTrip">Start one before recording deliveries.</span>
        <span v-else>Only driver logins can start trips.</span>
      </p>
      <Button v-if="canStartTrip" theme="blue" variant="solid" @click="showStart = true">Start Trip</Button>
    </div>

    <TripStartDialog v-model="showStart" @started="onChanged" />
    <TripCloseDialog v-model="showClose" :trip="activeTrip.data" @closed="onChanged" />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import TripStartDialog from '@/components/TripStartDialog.vue'
import TripCloseDialog from '@/components/TripCloseDialog.vue'
import { session } from '@/utils/session'

const emit = defineEmits(['change', 'update:hasTrip'])

const showStart = ref(false)
const showClose = ref(false)
const canStartTrip = computed(() => (session.data?.roles || []).includes('Sales User'))

const activeTrip = createResource({
  url: 'neer_jal.api.trip.get_active_trip',
  auto: true,
})

watch(
  () => activeTrip.data,
  (data) => emit('update:hasTrip', !!data),
  { immediate: true },
)

function onChanged() {
  activeTrip.reload()
  emit('change')
}
</script>
