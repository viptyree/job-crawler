import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '仪表盘', icon: 'Odometer' },
  },
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('../views/RuleManager.vue'),
    meta: { title: '规则管理', icon: 'Setting' },
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/TaskManager.vue'),
    meta: { title: '任务管理', icon: 'List' },
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('../views/DataCenter.vue'),
    meta: { title: '数据中心', icon: 'Coin' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('../views/Analysis.vue'),
    meta: { title: '行业分析', icon: 'TrendCharts' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: '系统设置', icon: 'Tools' },
  },
  {
    path: '/company-intel',
    name: 'CompanyIntel',
    redirect: '/company-intel/search',
    meta: { title: '企业招聘情报', icon: 'OfficeBuilding' },
    children: [
      {
        path: '/company-intel/search',
        name: 'CompanyIntelSearch',
        component: () => import('../views/company-intel/CompanySearch.vue'),
        meta: { title: '公司查询', icon: 'Search' },
      },
      {
        path: '/company-intel/companies',
        name: 'CompanyIntelCompanies',
        component: () => import('../views/company-intel/CompanyList.vue'),
        meta: { title: '公司档案', icon: 'OfficeBuilding' },
      },
      {
        path: '/company-intel/companies/:id',
        name: 'CompanyIntelCompanyProfile',
        component: () => import('../views/company-intel/CompanyProfile.vue'),
        meta: { title: '公司详情', hidden: true },
      },
      {
        path: '/company-intel/tasks',
        name: 'CompanyIntelTasks',
        component: () => import('../views/company-intel/CompanyQueryTasks.vue'),
        meta: { title: '查询任务', icon: 'Tickets' },
      },
      {
        path: '/company-intel/reports/:queryId',
        name: 'CompanyIntelReport',
        component: () => import('../views/company-intel/CompanyReport.vue'),
        meta: { title: '招聘报告', icon: 'Document' },
      },
      {
        path: '/company-intel/platform-accounts',
        name: 'CompanyIntelPlatformAccounts',
        component: () => import('../views/company-intel/PlatformAccounts.vue'),
        meta: { title: '平台账号', icon: 'User' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '招聘爬虫'} - 招聘爬虫管理系统`
})

export default router
export { routes }
