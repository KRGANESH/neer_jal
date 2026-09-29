<template>
  <Dialog v-model="show" :options="{ title: 'New Delivery', size: 'lg' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormControl
          v-if="!fixedCustomer"
          class="sm:col-span-2"
          type="select"
          label="Customer"
          required
          :options="customerOptions"
          v-model="form.customer"
        />
        <FormControl v-else class="sm:col-span-2" label="Customer" :model-value="fixedCustomerLabel" disabled />

        <FormControl type="date" label="Date" v-model="form.sales_date" />
        <FormControl
          type="select"
          label="Payment Mode"
          :options="['Cash', 'UPI', 'Pending', 'LCR', 'Free']"
          v-model="form.payment_mode"
        />

        <template v-if="noCansToReturn">
          <div class="sm:col-span-2 rounded border border-orange-200 bg-orange-50 px-3 py-2 text-sm text-orange-700">
            Customer currently holds 0 cans — nothing to return. {{ cansGiven }} can(s) will be delivered.
          </div>
        </template>
        <template v-else>
          <FormControl
            type="number"
            label="Refill"
            v-model="form.cans_returned"
            :description="`Empty cans collected. Max: ${currentPending} (customer's current pending cans)`"
          />
          <div class="flex flex-col justify-end text-sm text-gray-500">
            Cans to deliver: <span class="font-medium text-gray-900">{{ cansGiven }}</span>
          </div>
        </template>

        <FormControl type="number" label="Rate per Can" v-model="form.rate_per_can" />
        <div class="flex flex-col justify-end text-sm text-gray-500">
          Amount: <span class="font-medium text-gray-900">{{ amount }}</span>
        </div>

        <FormControl
          class="sm:col-span-2"
          type="textarea"
          label="Notes"
          v-model="form.notes"
        />
      </div>
      <p v-if="form.payment_mode === 'Pending'" class="mt-3 text-xs text-orange-500">
        This amount will be added to the customer's pending dues (company's responsibility to collect).
      </p>
      <p v-if="form.payment_mode === 'LCR'" class="mt-3 text-xs text-orange-500">
        This amount becomes the driver's personal responsibility to collect and settle later - it will
        not be added to the customer's company dues.
      </p>
      <ErrorMessage class="mt-3 block" :message="listResource.insert.error" />
    </template>
    <template #actions>
      <Button
        theme="blue" variant="solid"
        class="w-full"
        :loading="listResource.insert.loading"
        @click="submit"
      >
        Save Delivery
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createListResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  listResource: { type: Object, required: true },
  fixedCustomer: { type: String, default: '' },
  fixedCustomerLabel: { type: String, default: '' },
  fixedCustomerRate: { type: [Number, String], default: 0 },
  fixedCustomerCansRequired: { type: [Number, String], default: 0 },
  fixedCustomerCansPending: { type: [Number, String], default: 0 },
})
const emit = defineEmits(['update:modelValue', 'created'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const customers = createListResource({
  doctype: 'Customer',
  fields: ['name', 'customer_code', 'customer_name', 'rate_per_can', 'cans_required', 'cans_pending'],
  filters: { disabled: 0 },
  orderBy: 'customer_name asc',
  pageLength: 100,
  auto: !props.fixedCustomer,
})

const customerOptions = computed(() => {
  return (customers.data || []).map((c) => ({
    label: `${c.customer_code ? c.customer_code + ' - ' : ''}${c.customer_name}`,
    value: c.name,
  }))
})

function today() {
  return new Date().toISOString().slice(0, 10)
}

function emptyForm() {
  return {
    customer: props.fixedCustomer || '',
    cans_returned: 0,
    rate_per_can: props.fixedCustomer ? Number(props.fixedCustomerRate) || 0 : 0,
    sales_date: today(),
    payment_mode: 'Cash',
    notes: '',
  }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

const selectedCustomer = computed(() => {
  if (props.fixedCustomer) {
    return { cans_required: props.fixedCustomerCansRequired, cans_pending: props.fixedCustomerCansPending }
  }
  return customers.data?.find((c) => c.name === form.customer) || null
})

const target = computed(() => Number(selectedCustomer.value?.cans_required) || 0)
const currentPending = computed(() => Number(selectedCustomer.value?.cans_pending) || 0)
const noCansToReturn = computed(() => !!form.customer && currentPending.value === 0)
const cansGiven = computed(() =>
  Math.max(0, target.value - currentPending.value + (Number(form.cans_returned) || 0)),
)

// auto-fill the customer's default rate when picked from the dropdown
watch(
  () => form.customer,
  (name) => {
    if (props.fixedCustomer || !name) return
    const found = customers.data?.find((c) => c.name === name)
    if (found) form.rate_per_can = found.rate_per_can || 0
    form.cans_returned = 0
  },
)

const amount = computed(() => {
  const value = cansGiven.value * (Number(form.rate_per_can) || 0)
  return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

function submit() {
  if (!form.customer) {
    showError('Please select a customer')
    return
  }
  if (!noCansToReturn.value && Number(form.cans_returned) > currentPending.value) {
    showError(`Refill cannot exceed the ${currentPending.value} can(s) this customer currently holds`)
    return
  }
  props.listResource.insert.submit(
    { ...form },
    {
      onSuccess(doc) {
        showSuccess('Delivery recorded')
        show.value = false
        emit('created', doc)
      },
      onError(error) {
        showError(error, 'Could not save delivery')
      },
    },
  )
}
</script>
