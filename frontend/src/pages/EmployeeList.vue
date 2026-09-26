<template>
  <div class="mx-auto max-w-4xl p-4 sm:p-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Employees</h1>
        <p class="text-sm text-gray-500">Staff, sales team logins and office staff logins</p>
      </div>
      <Button theme="blue" variant="solid" class="w-full sm:w-auto" @click="showNewDialog = true">
        + New Employee
      </Button>
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead class="border-b bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Employee ID</th>
            <th class="px-4 py-3 font-medium">Name</th>
            <th class="px-4 py-3 font-medium">Phone</th>
            <th class="px-4 py-3 font-medium">Role</th>
            <th class="px-4 py-3 font-medium">Hourly Wage</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in employees.data" :key="row.name" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600">{{ row.employee_code }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ row.employee_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ row.phone || '-' }}</td>
            <td class="px-4 py-3">
              <Badge :theme="roleTheme(row.role)" variant="subtle">{{ row.role || 'Others' }}</Badge>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ formatCurrency(row.hourly_wage) }}</td>
            <td class="px-4 py-3">
              <Badge :theme="row.disabled ? 'gray' : 'green'" variant="subtle">
                {{ row.disabled ? 'Disabled' : 'Active' }}
              </Badge>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-2">
                <Button theme="blue" variant="outline" @click="openEdit(row)">Edit</Button>
                <Button v-if="row.user" theme="blue" variant="outline" @click="openResetPassword(row)">
                  Reset Password
                </Button>
                <Button theme="red" variant="outline" @click="openDeleteDialog(row)">Delete</Button>
              </div>
            </td>
          </tr>
          <tr v-if="!employees.list.loading && !employees.data?.length">
            <td colspan="7" class="px-4 py-10 text-center text-gray-400">No employees added yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex justify-center gap-2" v-if="employees.hasPreviousPage || employees.hasNextPage">
      <Button theme="blue" variant="outline" :disabled="!employees.hasPreviousPage" @click="employees.previous()">
        Previous
      </Button>
      <Button theme="blue" variant="outline" :disabled="!employees.hasNextPage" @click="employees.next()">
        Next
      </Button>
    </div>

    <EmployeeFormDialog v-model="showNewDialog" @created="employees.reload()" />
    <EmployeeEditDialog v-model="showEditDialog" :employee="editingEmployee" @updated="employees.reload()" />
    <ResetPasswordDialog
      v-model="showResetDialog"
      :user="selectedEmployee?.user"
      :user-label="selectedEmployee?.employee_name"
    />
    <Dialog v-model="showDeleteDialog" :options="{ title: 'Delete Employee', size: 'sm' }">
      <template #body-content>
        <p class="text-sm text-gray-600">
          Delete <span class="font-medium text-gray-900">{{ selectedEmployee?.employee_name }}</span> permanently?
          This will also delete their login, time logs, salary advances, sales entries, payment entries, and trips.
          This action cannot be undone.
        </p>
        <ErrorMessage class="mt-3 block" :message="deleteEmployee.error" />
      </template>
      <template #actions>
        <Button theme="red" variant="solid" class="w-full" :loading="deleteEmployee.loading" @click="confirmDelete">
          Delete Employee Permanently
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Badge, Button, createListResource, createResource, Dialog, ErrorMessage } from 'frappe-ui'
import EmployeeFormDialog from '@/components/EmployeeFormDialog.vue'
import EmployeeEditDialog from '@/components/EmployeeEditDialog.vue'
import ResetPasswordDialog from '@/components/ResetPasswordDialog.vue'
import { showError, showSuccess } from '@/utils/toast'

const showNewDialog = ref(false)
const showEditDialog = ref(false)
const showResetDialog = ref(false)
const showDeleteDialog = ref(false)
const editingEmployee = ref(null)
const selectedEmployee = ref(null)

const employees = createListResource({
  doctype: 'Employee',
  fields: [
    'name',
    'employee_code',
    'employee_name',
    'phone',
    'role',
    'user',
    'hourly_wage',
    'notes',
    'disabled',
    'dob',
    'gender',
    'email',
    'joining_date',
    'relieving_date',
    'employment_type',
    'status',
    'designation',
    'current_address',
    'permanent_address',
    'pincode',
    'state',
    'id_number',
    'emergency_contact',
    'education',
    'bank_name',
    'account_no',
    'ifsc_code',
    'other_bank_details',
  ],
  orderBy: 'employee_code asc',
  pageLength: 10,
  auto: true,
})

const deleteEmployee = createResource({
  url: 'neer_jal.api.employees.delete_employee',
})

function openEdit(row) {
  editingEmployee.value = row
  showEditDialog.value = true
}

function openResetPassword(row) {
  selectedEmployee.value = row
  showResetDialog.value = true
}

function openDeleteDialog(row) {
  selectedEmployee.value = row
  showDeleteDialog.value = true
}

function confirmDelete() {
  if (!selectedEmployee.value) return
  deleteEmployee.submit(
    { name: selectedEmployee.value.name },
    {
      onSuccess() {
        showDeleteDialog.value = false
        showSuccess('Employee and associated records deleted')
        selectedEmployee.value = null
        employees.reload()
      },
      onError(error) {
        showError(error, 'Could not delete employee')
      },
    },
  )
}

function roleTheme(role) {
  return { 'Sales Person': 'blue', 'Office Staff': 'orange' }[role] || 'gray'
}

function formatCurrency(value) {
  return (Number(value) || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
