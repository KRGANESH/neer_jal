<template>
  <div class="flex h-screen w-screen flex-col overflow-hidden bg-gray-50 text-gray-900 md:flex-row">
    <!-- mobile top bar -->
    <div class="flex shrink-0 items-center gap-2 border-b bg-white px-4 py-3 md:hidden">
      <button
        class="flex h-8 w-8 items-center justify-center rounded hover:bg-gray-100"
        @click="mobileMenuOpen = true"
        aria-label="Open menu"
      >
        <FeatherIcon name="menu" class="h-5 w-5 text-gray-600" />
      </button>
      <div class="flex h-6 w-6 items-center justify-center rounded bg-blue-600 text-xs font-bold text-white">
        N
      </div>
      <span class="text-base font-semibold">Neer Jal</span>
    </div>

    <!-- backdrop for mobile drawer -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 z-20 bg-black/40 md:hidden"
      @click="mobileMenuOpen = false"
    />

    <aside
      class="fixed inset-y-0 left-0 z-30 flex w-64 shrink-0 -translate-x-full flex-col border-r bg-white transition-transform duration-200 md:static md:z-auto md:w-56 md:translate-x-0"
      :class="{ 'translate-x-0': mobileMenuOpen }"
    >
      <div class="flex items-center justify-between gap-2 border-b px-4 py-4">
        <div class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded bg-blue-600 text-sm font-bold text-white">
            N
          </div>
          <span class="text-base font-semibold">Neer Jal</span>
        </div>
        <button
          class="flex h-7 w-7 items-center justify-center rounded hover:bg-gray-100 md:hidden"
          @click="mobileMenuOpen = false"
          aria-label="Close menu"
        >
          <FeatherIcon name="x" class="h-4 w-4 text-gray-600" />
        </button>
      </div>
      <nav class="flex-1 space-y-1 p-2">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-2 rounded px-3 py-2 text-sm font-medium text-gray-600 hover:bg-blue-50"
          :class="{ 'bg-blue-600 !text-white hover:bg-blue-600': isActive(item.to) }"
          @click="mobileMenuOpen = false"
        >
          {{ item.label }}
        </router-link>
      </nav>
      <div class="border-t p-3 text-xs text-gray-500">
        <div v-if="user.data" class="truncate">{{ user.data }}</div>
        <button class="mt-1 text-red-500 hover:underline" @click="logout">Log out</button>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>
    <Toasts />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, call, FeatherIcon, Toasts } from 'frappe-ui'
import { isManager, isHrManager } from '@/utils/session'

const route = useRoute()
const mobileMenuOpen = ref(false)

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false
  },
)

const navItems = computed(() => {
  // A pure Office Staff user (no manager role) only needs the HR tabs -
  // give them just those instead of the sales-oriented nav.
  if (isHrManager.value && !isManager.value) {
    return [
      { label: 'Time Clock', to: '/time-clock' },
      { label: 'Salary Advances', to: '/salary-advances' },
      { label: 'Payroll', to: '/payroll' },
    ]
  }

  const items = [
    { label: 'Sales', to: '/sales' },
    { label: 'Customers', to: '/customers' },
    { label: 'Trips', to: '/trips' },
  ]
  if (isManager.value) {
    items.push(
      { label: 'Vehicles', to: '/vehicles' },
      { label: 'Trip Routes', to: '/trip-routes' },
      { label: 'Employees', to: '/employees' },
      { label: 'Reports', to: '/reports' },
      { label: 'LCR', to: '/lcr' },
      { label: 'Settings', to: '/settings' },
    )
  }
  if (isHrManager.value) {
    items.push(
      { label: 'Time Clock', to: '/time-clock' },
      { label: 'Salary Advances', to: '/salary-advances' },
      { label: 'Payroll', to: '/payroll' },
    )
  }
  return items
})

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}

const user = createResource({
  url: 'frappe.auth.get_logged_user',
  auto: true,
})

function logout() {
  call('logout').then(() => {
    window.location.href = '/login'
  })
}
</script>
