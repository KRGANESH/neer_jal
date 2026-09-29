<template>
  <Dialog v-model="show" :options="{ title: 'Settle LCR', size: 'sm' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4">
        <FormControl
          type="select"
          label="Driver"
          required
          :options="salesPersonOptions"
          v-model="form.sales_person"
        />
        <FormControl
          type="select"
          label="Customer"
          required
          :options="customerOptions"
          v-model="form.customer"
        />
        <FormControl
          label="LCR Amount Pending"
          disabled
          :model-value="due.loading ? 'Loading...' : formatCurrency(due.data?.amount)"
        />
        <FormControl
          type="select"
          label="Received Via"
          required
          :options="['Cash', 'UPI']"
          v-model="form.payment_mode"
        />
        <FormControl type="date" label="Date" v-model="form.payment_date" />
        <FormControl type="textarea" label="Notes" v-model="form.notes" />
      </div>
      <p class="mt-3 text-xs text-gray-400">
        This marks the selected driver's LCR for this customer as settled.
      </p>
      <ErrorMessage class="mt-3 block" :message="settle.error" />
    </template>
    <template #actions>
      <Button
        theme="blue"
        variant="solid"
        class="w-full"
        :loading="settle.loading"
        :disabled="!due.data?.amount"
        @click="submit"
      >
        Settle LCR
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createResource, createListResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  prefillSalesPerson: { type: String, default: '' },
  prefillCustomer: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'settled'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function today() {
  return new Date().toISOString().slice(0, 10)
}

function emptyForm() {
  return {
    sales_person: props.prefillSalesPerson || '',
    customer: props.prefillCustomer || '',
    payment_mode: 'Cash',
    payment_date: today(),
    notes: '',
  }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

const customers = createListResource({
  doctype: 'Customer',
  fields: ['name', 'customer_code', 'customer_name'],
  orderBy: 'customer_name asc',
  pageLength: 200,
  auto: true,
})

const salesPersons = createResource({
  url: 'neer_jal.api.users.list_sales_users',
  auto: true,
  params: { start: 0, page_length: 200 },
  initialData: [],
})

const customerOptions = computed(() => [
  { label: 'Select a customer', value: '' },
  ...(customers.data || []).map((c) => ({ label: `${c.customer_code ? c.customer_code + ' - ' : ''}${c.customer_name}`, value: c.name })),
])

const salesPersonOptions = computed(() => [
  { label: 'Select a driver', value: '' },
  ...(salesPersons.data || []).map((u) => ({ label: u.full_name, value: u.name })),
])

const due = createResource({
  url: 'neer_jal.api.settlement.get_lcr_due',
})

watch(
  [() => form.sales_person, () => form.customer],
  ([salesPerson, customer]) => {
    if (salesPerson && customer) {
      due.submit({ sales_person: salesPerson, customer })
    } else {
      due.reset()
    }
  },
  { immediate: true },
)

const settle = createResource({
  url: 'neer_jal.api.settlement.settle_lcr',
})

function submit() {
  if (!form.sales_person || !form.customer) {
    showError('Please select a sales person and a customer')
    return
  }
  settle.submit(
    { ...form },
    {
      onSuccess() {
        showSuccess('LCR settled')
        show.value = false
        emit('settled')
      },
      onError(error) {
        showError(error, 'Could not settle LCR')
      },
    },
  )
}

function formatCurrency(value) {
  if (value === undefined || value === null) return '-'
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
