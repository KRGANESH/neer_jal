<template>
  <div class="mx-auto max-w-4xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">LCR</h1>
        <p class="text-sm text-gray-500">
          Money a driver personally took responsibility for collecting from a customer
        </p>
      </div>
      <Button theme="blue" variant="solid" class="w-full sm:w-auto" @click="openSettleFresh">
        Settle LCR
      </Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[560px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Driver</th>
            <th class="px-4 py-3 font-medium">Customer</th>
            <th class="px-4 py-3 font-medium">Amount Pending</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in lcr.data" :key="`${row.sales_person}-${row.customer}`" class="border-b last:border-0">
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.sales_person }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.customer_name || row.customer }}</td>
            <td class="px-4 py-3">
              <Badge theme="orange" variant="subtle">{{ formatCurrency(row.amount) }}</Badge>
            </td>
            <td class="px-4 py-3">
              <Button theme="blue" variant="outline" @click="openSettle(row)">Settle</Button>
            </td>
          </tr>
          <tr v-if="!lcr.loading && !lcr.data?.length">
            <td colspan="4" class="px-4 py-10 text-center text-gray-400">
              No outstanding LCR amounts
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <SettleLcrDialog
      v-model="showSettleDialog"
      :prefill-sales-person="prefill.sales_person"
      :prefill-customer="prefill.customer"
      @settled="lcr.reload()"
    />
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { Button, Badge, createResource } from 'frappe-ui'
import SettleLcrDialog from '@/components/SettleLcrDialog.vue'

const showSettleDialog = ref(false)
const prefill = reactive({ sales_person: '', customer: '' })

const lcr = createResource({
  url: 'neer_jal.api.settlement.get_lcr_summary',
  auto: true,
  initialData: [],
})

function openSettle(row) {
  prefill.sales_person = row.sales_person
  prefill.customer = row.customer
  showSettleDialog.value = true
}

function openSettleFresh() {
  prefill.sales_person = ''
  prefill.customer = ''
  showSettleDialog.value = true
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
