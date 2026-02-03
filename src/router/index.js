
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue' // 首页
import CreateSpace from '../views/CreateSpace.vue' // 创作空间详情页
import SubscribeLink from '../views/SubscribeLink.vue' // 订阅链接页
import LibraryRoom from '../views/LibraryRoom.vue'
import UserInfo from '../views/UserInfo.vue' 

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
    meta: { requiresAuth: true } 
  },
  {
    path: '/SubscribeLink',
    name: 'SubscribeLink',
    component: SubscribeLink,
    meta: { requiresAuth: true } 
  },
  {
    path: '/LibraryRoom',
    name: 'LibraryRoom',
    component: LibraryRoom,
    meta: { requiresAuth: true } 
  },
  {
    path: '/UserInfo',
    name: 'UserInfo',
    component: UserInfo,
    meta: { requiresAuth: true } 
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