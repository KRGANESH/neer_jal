<template>
  <Dialog v-model="show" :options="{ title: 'New Employee', size: 'lg' }">
    <template #body-content>
      <div class="boxed-fields grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormControl class="sm:col-span-2" label="Employee Name" required v-model="form.employee_name" />
        <FormControl type="date" label="Date of Birth" v-model="form.dob" />
        <FormControl type="select" label="Gender" :options="genderOptions" v-model="form.gender" />
        <FormControl
          label="Phone"
          v-model="form.phone"
          maxlength="10"
          description="10-digit phone number (optional)"
        />
        <FormControl label="Email" v-model="form.email" />
        <FormControl type="number" label="Hourly Wage" v-model="form.hourly_wage" />
        <FormControl label="Designation" v-model="form.designation" />
        <FormControl
          type="select"
          label="Employment Type"
          :options="employmentTypeOptions"
          v-model="form.employment_type"
        />
        <FormControl
          class="sm:col-span-2"
          type="select"
          label="Role"
          :options="roleOptions"
          v-model="form.role"
          description="Leave as 'Others' for a normal employee. Only Driver and Office Staff get an app login."
        />
        <template v-if="form.role">
          <FormControl
            label="Username"
            required
            v-model="form.username"
            description="Lowercase letters, numbers, dots, underscores or hyphens only. This becomes their login."
          />
          <FormControl
            type="password"
            label="Password"
            required
            v-model="form.password"
            description="Avoid common or easily guessed passwords. Share this with the employee."
          />
        </template>

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Address & ID
        </div>
        <FormControl type="textarea" label="Current Address" v-model="form.current_address" />
        <FormControl type="textarea" label="Permanent Address" v-model="form.permanent_address" />
        <FormControl
          label="Pincode"
          v-model="form.pincode"
          maxlength="6"
          description="6-digit postal PIN code (optional)"
        />
        <FormControl label="State" v-model="form.state" />
        <FormControl
          label="ID Number"
          v-model="form.id_number"
          description="e.g. Aadhaar number (optional)"
        />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Emergency & Education
        </div>
        <FormControl label="Emergency Contact" v-model="form.emergency_contact" />
        <FormControl label="Education" v-model="form.education" />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Bank Details
        </div>
        <FormControl label="Bank" v-model="form.bank_name" />
        <FormControl label="Account No" v-model="form.account_no" />
        <FormControl label="IFSC Code" v-model="form.ifsc_code" />
        <FormControl label="Others" v-model="form.other_bank_details" />

        <div class="sm:col-span-2 mt-1 border-t pt-4 text-sm font-semibold text-gray-500">
          Notes
        </div>
        <FormControl class="sm:col-span-2" type="textarea" label="Notes" v-model="form.notes" />
      </div>
      <ErrorMessage class="mt-3 block" :message="create.error" />
    </template>
    <template #actions>
      <Button theme="blue" variant="solid" class="w-full" :loading="create.loading" @click="submit">
        Create Employee
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Dialog, FormControl, Button, ErrorMessage, createResource } from 'frappe-ui'
import { showSuccess, showError } from '@/utils/toast'
import { checkPasswordStrength } from '@/utils/password'
import { checkPhoneNumber } from '@/utils/phone'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'created'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const roleOptions = [
  { label: 'Others (no login)', value: '' },
  { label: 'Driver', value: 'Driver' },
  { label: 'Office Staff', value: 'Office Staff' },
]

const genderOptions = [
  { label: '', value: '' },
  { label: 'Male', value: 'Male' },
  { label: 'Female', value: 'Female' },
  { label: 'Other', value: 'Other' },
]

const employmentTypeOptions = [
  { label: '', value: '' },
  { label: 'Full-time', value: 'Full-time' },
  { label: 'Part-time', value: 'Part-time' },
  { label: 'Contract', value: 'Contract' },
  { label: 'Daily Wage', value: 'Daily Wage' },
]

function emptyForm() {
  return {
    employee_name: '',
    dob: '',
    gender: '',
    phone: '',
    email: '',
    hourly_wage: 0,
    designation: '',
    employment_type: '',
    role: '',
    username: '',
    password: '',
    current_address: '',
    permanent_address: '',
    pincode: '',
    state: '',
    id_number: '',
    emergency_contact: '',
    education: '',
    bank_name: '',
    account_no: '',
    ifsc_code: '',
    other_bank_details: '',
    notes: '',
  }
}

let form = reactive(emptyForm())

watch(show, (value) => {
  if (value) Object.assign(form, emptyForm())
})

const create = createResource({
  url: 'neer_jal.api.employees.create_employee',
})

function submit() {
  if (!form.employee_name) {
    showError('Employee name is required')
    return
  }
  if (form.phone) {
    const phoneError = checkPhoneNumber(form.phone)
    if (phoneError) {
      showError(phoneError)
      return
    }
  }
  if (form.pincode && !/^\d{6}$/.test(form.pincode)) {
    showError('Pincode must be exactly 6 digits')
    return
  }
  if (form.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
    showError('Enter a valid email address')
    return
  }
  if (form.role) {
    if (!form.username || !form.password) {
      showError('Username and password are required for this role')
      return
    }
    const passwordError = checkPasswordStrength(form.password, {
      inputs: [form.employee_name, form.username],
    })
    if (passwordError) {
      showError(passwordError)
      return
    }
  }
  create.submit(
    { ...form },
    {
      onSuccess() {
        showSuccess('Employee created')
        show.value = false
        emit('created')
      },
      onError(error) {
        showError(error, 'Could not create employee')
      },
    },
  )
}
</script>
