<template>
  <div class="mx-auto max-w-5xl p-4 sm:p-6" v-if="customer.doc">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <router-link to="/customers" class="text-sm text-gray-500 hover:underline">
          &larr; Customers
        </router-link>
        <h1 class="mt-1 text-2xl font-semibold text-gray-900">
          {{ customer.doc.customer_name }}
          <span class="text-base font-medium text-gray-400">#{{ customer.doc.customer_code }}</span>
        </h1>
        <p class="text-sm text-gray-500">{{ customer.doc.name }} &middot; {{ customer.doc.phone }}</p>
      </div>
      <Button
        v-if="isManager"
        theme="blue" variant="solid"
        class="w-full sm:w-auto"
        :loading="customer.save.loading"
        :disabled="!hasChanges"
        @click="saveChanges"
      >
        Save Changes
      </Button>
    </div>

    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="rounded-lg border bg-white p-5">
        <p class="text-xs font-semibold uppercase text-gray-500">Cans Pending with Customer</p>
        <p class="mt-1 text-3xl font-semibold" :class="customer.doc.cans_pending > 0 ? 'text-orange-500' : 'text-gray-900'">
          {{ customer.doc.cans_pending || 0 }}
        </p>
      </div>
      <div class="rounded-lg border bg-white p-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-xs font-semibold uppercase text-gray-500">Amount Due</p>
            <p class="mt-1 text-3xl font-semibold" :class="customer.doc.amount_due > 0 ? 'text-red-500' : 'text-gray-900'">
              {{ formatCurrency(customer.doc.amount_due) }}
            </p>
          </div>
          <Button v-if="customer.doc.amount_due > 0" theme="blue" variant="outline" @click="showSettleDue = true">
            Settle Due
          </Button>
        </div>
      </div>
    </div>

    <div class="mb-8 rounded-lg border bg-white p-5">
      <h2 class="mb-4 text-sm font-semibold uppercase text-gray-500">Customer Details</h2>
      <div
        class="boxed-fields grid grid-cols-1 gap-4 sm:grid-cols-2"
        @input="hasChanges = true"
        @change="hasChanges = true"
      >
        <FormControl label="Customer ID" disabled :model-value="customer.doc.customer_code" />
        <FormControl label="Customer Name" :disabled="!isManager" v-model="customer.doc.customer_name" />
        <FormControl
          label="Phone"
          :disabled="!isManager"
          v-model="customer.doc.phone"
          maxlength="10"
          description="10-digit phone number"
        />
        <FormControl class="sm:col-span-2" type="textarea" label="Address" :disabled="!isManager" v-model="customer.doc.address_line" />
        <FormControl label="City / Area" :disabled="!isManager" v-model="customer.doc.city" />
        <FormControl type="checkbox" label="Disabled" :disabled="!isManager" v-model="customer.doc.disabled" />
        <FormControl
          type="checkbox"
          label="Send SMS notifications for deliveries"
          :disabled="!isManager"
          v-model="customer.doc.sms_enabled"
        />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Water Can Settings
        </div>
        <FormControl
          type="number"
          label="Cans Required (per delivery)"
          :disabled="!isManager"
          v-model="customer.doc.cans_required"
        />
        <FormControl
          type="number"
          label="Rate per Can"
          :disabled="!isManager"
          v-model="customer.doc.rate_per_can"
        />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Notes
        </div>
        <FormControl
          class="sm:col-span-2"
          type="textarea"
          label="Notes"
          :disabled="!isManager"
          v-model="customer.doc.notes"
        />
      </div>
      <p v-if="!isManager" class="mt-3 text-xs text-gray-400">
        Only a Sales Manager can edit customer details and can/rate settings.
      </p>
    </div>

    <div class="rounded-lg border bg-white">
      <div class="flex flex-col gap-3 border-b p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-sm font-semibold uppercase text-gray-500">Deliveries</h2>
          <p class="text-xs text-gray-400">{{ sales.data?.length || 0 }} delivery(ies) for this customer</p>
        </div>
        <Button theme="blue" variant="solid" class="w-full sm:w-auto" @click="showNewSale = true">+ New Delivery</Button>
      </div>
      <div class="overflow-x-auto">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Given</th>
            <th class="px-4 py-3 font-medium">Refill</th>
            <th class="px-4 py-3 font-medium">Rate</th>
            <th class="px-4 py-3 font-medium">Amount</th>
            <th class="px-4 py-3 font-medium">Payment</th>
            <th class="px-4 py-3 font-medium">Driver</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in sales.data" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600">{{ row.sales_date }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.cans_given }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.cans_returned }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.rate_per_can }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.amount }}</td>
            <td class="px-4 py-3">
              <Badge :theme="paymentTheme(row.payment_mode)" variant="subtle">{{ row.payment_mode }}</Badge>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ row.sales_person }}</td>
          </tr>
          <tr v-if="!sales.list.loading && !sales.data?.length">
            <td colspan="7" class="px-4 py-10 text-center text-gray-400">
              No deliveries recorded yet for this customer
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

    <div class="mt-8 rounded-lg border bg-white">
      <div class="border-b p-5">
        <h2 class="text-sm font-semibold uppercase text-gray-500">Payments</h2>
        <p class="text-xs text-gray-400">{{ payments.data?.length || 0 }} settlement(s) recorded</p>
      </div>
      <div class="overflow-x-auto">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Date</th>
            <th class="px-4 py-3 font-medium">Amount</th>
            <th class="px-4 py-3 font-medium">Mode</th>
            <th class="px-4 py-3 font-medium">Driver LCR Settled For</th>
            <th class="px-4 py-3 font-medium">Received By</th>
            <th class="px-4 py-3 font-medium">Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in payments.data" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600">{{ row.payment_date }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ formatCurrency(row.amount) }}</td>
            <td class="px-4 py-3">
              <Badge :theme="row.payment_mode === 'UPI' ? 'blue' : 'green'" variant="subtle">
                {{ row.payment_mode }}
              </Badge>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ row.sales_person || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.received_by }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.notes || '-' }}</td>
          </tr>
          <tr v-if="!payments.list.loading && !payments.data?.length">
            <td colspan="6" class="px-4 py-10 text-center text-gray-400">
              No payments recorded yet for this customer
            </td>
          </tr>
        </tbody>
      </table>
      </div>
      <div class="flex justify-center gap-2 border-t p-4" v-if="payments.hasPreviousPage || payments.hasNextPage">
        <Button theme="blue" variant="outline" :disabled="!payments.hasPreviousPage" @click="payments.previous()">
          Previous
        </Button>
        <Button theme="blue" variant="outline" :disabled="!payments.hasNextPage" @click="payments.next()">
          Next
        </Button>
      </div>
    </div>

    <SalesFormDialog
      v-model="showNewSale"
      :list-resource="sales"
      :fixed-customer="customer.doc.name"
      :fixed-customer-label="`${customer.doc.customer_name} (${customer.doc.name})`"
      :fixed-customer-rate="customer.doc.rate_per_can"
      :fixed-customer-cans-required="customer.doc.cans_required"
      :fixed-customer-cans-pending="customer.doc.cans_pending"
      @created="customer.reload()"
    />

    <PaymentFormDialog
      v-model="showSettleDue"
      :customer="customer.doc.name"
      :customer-label="`${customer.doc.customer_name} (${customer.doc.name})`"
      :current-due="customer.doc.amount_due"
      @settled="onSettled"
    />
  </div>
  <div v-else class="p-6 text-gray-400">Loading...</div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FormControl, Badge, createDocumentResource, createListResource } from 'frappe-ui'
import SalesFormDialog from '@/components/SalesFormDialog.vue'
import PaymentFormDialog from '@/components/PaymentFormDialog.vue'
import { isManager } from '@/utils/session'
import { showSuccess, showError } from '@/utils/toast'
import { checkPhoneNumber } from '@/utils/phone'

const props = defineProps({
  customerId: { type: String, required: true },
})

const showNewSale = ref(false)
const showSettleDue = ref(false)
const hasChanges = ref(false)

const customer = createDocumentResource({
  doctype: 'Customer',
  name: props.customerId,
})

function saveChanges() {
  if (customer.save.loading) return
  const phoneError = checkPhoneNumber(customer.doc.phone)
  if (phoneError) {
    showError(phoneError)
    return
  }
  customer.save.submit(null, {
    onSuccess() {
      hasChanges.value = false
      showSuccess('Customer updated')
    },
    onError(error) {
      if (error?.exc_type === 'TimestampMismatchError') {
        customer.reload()
        showError('Customer was changed elsewhere, reloaded the latest version. Please try again.')
        return
      }
      showError(error, 'Could not save changes')
    },
  })
}

const sales = createListResource({
  doctype: 'Sales Entry',
  fields: [
    'name',
    'sales_date',
    'cans_given',
    'cans_returned',
    'rate_per_can',
    'amount',
    'payment_mode',
    'sales_person',
  ],
  filters: { customer: props.customerId },
  orderBy: 'sales_date desc, creation desc',
  pageLength: 10,
  auto: true,
})

const payments = createListResource({
  doctype: 'Payment Entry',
  fields: ['name', 'payment_date', 'amount', 'payment_mode', 'sales_person', 'received_by', 'notes'],
  filters: { customer: props.customerId },
  orderBy: 'payment_date desc, creation desc',
  pageLength: 10,
  auto: true,
})

function paymentTheme(mode) {
  return { Cash: 'green', UPI: 'blue', Pending: 'red', LCR: 'orange', Free: 'gray' }[mode] || 'gray'
}

function onSettled() {
  customer.reload()
  sales.reload()
  payments.reload()
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
