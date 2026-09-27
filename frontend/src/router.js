import { createRouter, createWebHistory } from 'vue-router'
import { session } from './utils/session'

const routes = [
  {
    path: '/',
    redirect: '/sales',
  },
  {
    path: '/sales',
    name: 'SalesList',
    component: () => import('@/pages/SalesList.vue'),
  },
  {
    path: '/customers',
    name: 'CustomerList',
    component: () => import('@/pages/CustomerList.vue'),
  },
  {
    path: '/customers/:customerId',
    name: 'CustomerDetail',
    component: () => import('@/pages/CustomerDetail.vue'),
    props: true,
  },
  {
    path: '/vehicles',
    name: 'VehicleList',
    component: () => import('@/pages/VehicleList.vue'),
  },
  {
    path: '/employees',
    name: 'EmployeeList',
    component: () => import('@/pages/EmployeeList.vue'),
  },
  {
    path: '/time-clock',
    name: 'TimeClockList',
    component: () => import('@/pages/TimeClockList.vue'),
  },
  {
    path: '/time-clock/:employee',
    name: 'EmployeeTimeLogs',
    component: () => import('@/pages/EmployeeTimeLogs.vue'),
    props: true,
  },
  {
    path: '/payroll',
    name: 'PayrollReport',
    component: () => import('@/pages/PayrollReport.vue'),
  },
  {
    path: '/salary-advances',
    name: 'SalaryAdvanceList',
    component: () => import('@/pages/SalaryAdvanceList.vue'),
  },
  {
    path: '/trips',
    name: 'TripList',
    component: () => import('@/pages/TripList.vue'),
  },
  {
    path: '/trips/:tripId',
    name: 'TripDetail',
    component: () => import('@/pages/TripDetail.vue'),
    props: true,
  },
  {
    path: '/trip-routes',
    name: 'TripRouteList',
    component: () => import('@/pages/TripRouteList.vue'),
  },
  {
    path: '/reports',
    name: 'ReportsList',
    component: () => import('@/pages/ReportsList.vue'),
  },
  {
    path: '/lcr',
    name: 'LcrList',
    component: () => import('@/pages/LcrList.vue'),
  },
  {
    path: '/settings',
    name: 'SettingsPage',
    component: () => import('@/pages/SettingsPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/neer_jal'),
  routes,
})

// A pure Office Staff user (no manager role) only has the Time Clock tab -
// landing them on /sales (which they have no nav entry for, and no
// permission on) is confusing, so send them straight to their one page.
router.beforeEach(async (to, from) => {
  if (to.path === '/sales' && from.path === '/') {
    if (session.loading) await session.promise
    if (session.data?.is_hr_manager && !session.data?.is_manager) {
      return '/time-clock'
    }
  }
})

export default router
