<template>
  <div class="sidebar">
    <div class="logo">
      <span class="logo-icon">🕷</span>
      <span class="logo-text">招聘爬虫</span>
    </div>
    <el-menu
      :default-active="currentRoute"
      class="sidebar-menu"
      background-color="#1d1e1f"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <template v-for="route in menuRoutes" :key="route.path">
        <el-sub-menu v-if="visibleChildren(route).length" :index="route.path">
          <template #title>
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <span>{{ route.meta.title }}</span>
          </template>
          <el-menu-item v-for="child in visibleChildren(route)" :key="child.path" :index="child.path">
            <el-icon><component :is="child.meta.icon" /></el-icon>
            <span>{{ child.meta.title }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="route.path">
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <span>{{ route.meta.title }}</span>
        </el-menu-item>
      </template>
    </el-menu>
    <div class="sidebar-footer">
      <div class="version">v1.0.0</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { routes } from '@/router/index.js'

const route = useRoute()
const currentRoute = computed(() => route.path)
const menuRoutes = routes.filter(r => r.meta?.title)
const visibleChildren = (route) => (route.children || []).filter(child => child.meta?.title && !child.meta?.hidden)
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 220px;
  background-color: #1d1e1f;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #333;
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 2px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  font-size: 14px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #263445 !important;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #1890ff20 !important;
  border-right: 3px solid #409EFF;
}

.sidebar-footer {
  padding: 12px;
  text-align: center;
  border-top: 1px solid #333;
}

.version {
  color: #666;
  font-size: 12px;
}
</style>
