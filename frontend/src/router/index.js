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
