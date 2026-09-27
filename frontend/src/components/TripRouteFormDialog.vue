<template>
  <Dialog v-model="show" :options="{ title: route ? 'Edit Trip Route' : 'New Trip Route', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl label="Route Name" required v-model="form.route_name" />
        <FormControl type="number" label="Driver Trip Price" required v-model="form.route_price" />
      </div>
      <ErrorMessage class="mt-3 block" :message="routes.insert.error || routes.setValue.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="routes.insert.loading || routes.setValue.loading" @click="submit">
        Save
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  routes: { type: Object, required: true },
  route: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'created', 'updated'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function emptyForm() {
  return props.route
    ? { route_name: props.route.route_name, route_price: props.route.route_price }
    : { route_name: '', route_price: 0 }
}

const form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

function submit() {
  if (!form.route_name) {
    showError('Route name is required')
    return
  }
  if (Number(form.route_price) < 0) {
    showError('Driver trip price cannot be negative')
    return
  }

  const action = props.route ? props.routes.setValue : props.routes.insert
  const payload = props.route ? { name: props.route.name, ...form } : { ...form }
  action.submit(payload, {
    onSuccess() {
      showSuccess(props.route ? 'Trip route updated' : 'Trip route added')
      show.value = false
      emit(props.route ? 'updated' : 'created')
    },
    onError(error) {
      showError(error, props.route ? 'Could not update trip route' : 'Could not add trip route')
    },
  })
}
</script>
