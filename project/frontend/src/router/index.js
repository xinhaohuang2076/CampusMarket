import { createRouter, createWebHashHistory } from 'vue-router'
import { isAdmin } from '../utils/admin.js'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue'), meta: { title: '校园二手交易平台' } },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { title: '注册' } },
  { path: '/product/:id', name: 'ProductDetail', component: () => import('../views/ProductDetail.vue'), meta: { title: '商品详情' } },
  { path: '/product/new', name: 'NewProduct', component: () => import('../views/ProductForm.vue'), meta: { title: '发布商品', requiresAuth: true } },
  { path: '/product/:id/edit', name: 'EditProduct', component: () => import('../views/ProductForm.vue'), meta: { title: '编辑商品', requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { title: '个人中心', requiresAuth: true } },
  { path: '/my-products', name: 'MyProducts', component: () => import('../views/MyProducts.vue'), meta: { title: '我的商品', requiresAuth: true } },
  { path: '/favorites', name: 'Favorites', component: () => import('../views/Favorites.vue'), meta: { title: '我的收藏', requiresAuth: true } },
  { path: '/transactions', name: 'Transactions', component: () => import('../views/Transactions.vue'), meta: { title: '交易记录', requiresAuth: true } },
  { path: '/messages', name: 'Messages', component: () => import('../views/Messages.vue'), meta: { title: '我的留言', requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: () => import('../views/Admin.vue'), meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'CampusMarket'
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next('/login')
  } else if (to.meta.requiresAdmin && !isAdmin()) {
    next('/')
  } else {
    next()
  }
})

export default router
