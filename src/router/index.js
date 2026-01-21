
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue' // 首页
import CreateSpace from '../views/CreateSpace.vue' // 创作空间详情页

const routes = [
  {
    path: '/',
    name: 'HomeView',
    component: HomeView
  },
  {
    path: '/CreateSpace',
    name: 'CreateSpace',
    component: CreateSpace,
    meta: { requiresAuth: true } // 标记该页面需要登录才能访问
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫：判断是否登录（简单模拟，实际项目需结合后端token）
router.beforeEach((to, from, next) => {
  // 从localStorage获取toeken，判断是否登录状态
  const token = localStorage.getItem('userToken')
  if (to.meta.requiresAuth && !token) {
    alert('请先登录！')
    next('/') // 跳回首页
  } else {
    next() // 正常跳转
  }
})

export default router