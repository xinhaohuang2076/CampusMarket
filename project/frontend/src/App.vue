<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const showMobileMenu = ref(false)

function loadUser() {
  return JSON.parse(localStorage.getItem('user') || 'null')
}
const user = ref(loadUser())

const isLoggedIn = computed(() => !!user.value)
const initials = computed(() => {
  const name = user.value?.nickname || user.value?.student_id || ''
  return name.charAt(0).toUpperCase()
})

watch(route, () => {
  showMobileMenu.value = false
  user.value = loadUser()
})

onMounted(() => {
  window.addEventListener('user-changed', () => { user.value = loadUser() })
})

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-warm-50">
    <!-- 顶部导航 -->
    <nav class="bg-white/90 backdrop-blur-md border-b border-warm-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-4 sm:px-6">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-2.5 shrink-0 group">
            <div class="w-8 h-8 bg-coral-500 rounded-xl flex items-center justify-center transition-transform group-hover:scale-105">
              <svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
              </svg>
            </div>
            <span class="font-display font-bold text-xl text-slate-800 tracking-tight">Campus<span class="text-coral-500">Market</span></span>
          </router-link>

          <!-- 桌面导航 -->
          <div class="hidden md:flex items-center gap-1">
            <router-link to="/" class="nav-link" active-class="nav-link-active">首页</router-link>
            <router-link v-if="isLoggedIn" to="/product/new" class="nav-link" active-class="nav-link-active">发布</router-link>
            <router-link v-if="isLoggedIn" to="/my-products" class="nav-link" active-class="nav-link-active">我的商品</router-link>
            <router-link v-if="isLoggedIn" to="/transactions" class="nav-link" active-class="nav-link-active">交易</router-link>
            <router-link v-if="isLoggedIn && user?.role === 'admin'" to="/admin" class="nav-link" active-class="nav-link-active">管理后台</router-link>

            <div v-if="isLoggedIn" class="flex items-center gap-3 ml-4 pl-4 border-l border-warm-200">
              <router-link to="/favorites" class="text-slate-500 hover:text-coral-500 transition p-1.5 rounded-lg hover:bg-coral-50" title="收藏">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>
              </router-link>
              <router-link to="/messages" class="text-slate-500 hover:text-coral-500 transition p-1.5 rounded-lg hover:bg-coral-50" title="留言">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
                </svg>
              </router-link>
              <router-link to="/profile" class="flex items-center gap-2 text-sm text-slate-700 hover:text-coral-600 transition pl-2">
                <div class="w-7 h-7 bg-coral-100 text-coral-600 rounded-full flex items-center justify-center text-xs font-semibold">
                  {{ initials }}
                </div>
                <span class="font-medium max-w-[100px] truncate">{{ user?.nickname || user?.student_id }}</span>
              </router-link>
              <button @click="logout" class="text-sm text-slate-400 hover:text-coral-500 transition ml-1 p-1.5 rounded-lg hover:bg-coral-50" title="退出">
                <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                </svg>
              </button>
            </div>
            <div v-else class="flex items-center gap-2 ml-4 pl-4 border-l border-warm-200">
              <router-link to="/login" class="text-sm text-slate-600 hover:text-coral-600 transition px-3 py-1.5 rounded-lg hover:bg-coral-50">登录</router-link>
              <router-link to="/register" class="text-sm bg-coral-500 text-white px-4 py-1.5 rounded-lg hover:bg-coral-600 transition btn-press shadow-sm shadow-coral-200">注册</router-link>
            </div>
          </div>

          <!-- 移动端按钮 -->
          <button @click="showMobileMenu = !showMobileMenu" class="md:hidden p-2 text-slate-500 hover:text-coral-500 transition rounded-lg hover:bg-coral-50">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path v-if="!showMobileMenu" stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 移动端菜单 -->
        <div v-if="showMobileMenu" class="md:hidden pb-4 border-t border-warm-100 pt-3 text-sm space-y-1">
          <router-link to="/" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">首页</router-link>
          <template v-if="isLoggedIn">
            <router-link to="/product/new" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">发布商品</router-link>
            <router-link to="/my-products" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">我的商品</router-link>
            <router-link to="/transactions" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">交易记录</router-link>
            <router-link v-if="user?.role === 'admin'" to="/admin" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">管理后台</router-link>
            <router-link to="/favorites" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">收藏</router-link>
            <router-link to="/messages" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">留言</router-link>
            <router-link to="/profile" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">个人中心</router-link>
            <button @click="logout" class="block w-full text-left px-3 py-2 text-slate-400 rounded-lg hover:bg-coral-50 hover:text-coral-500">退出登录</button>
          </template>
          <template v-else>
            <router-link to="/login" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">登录</router-link>
            <router-link to="/register" class="block px-3 py-2 text-slate-600 rounded-lg hover:bg-coral-50 hover:text-coral-600">注册</router-link>
          </template>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <router-view v-slot="{ Component }">
        <transition name="slide-up" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 底部 -->
    <footer class="text-center py-8 mt-16">
      <div class="max-w-6xl mx-auto px-4 border-t border-warm-200 pt-6">
        <p class="text-xs text-slate-400">CampusMarket 校园二手交易平台</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.nav-link {
  position: relative;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-slate-600);
  border-radius: 0.5rem;
  transition: all 0.2s;
}
.nav-link:hover {
  color: var(--color-coral-600);
  background-color: var(--color-coral-50);
}
.nav-link-active {
  color: var(--color-coral-600) !important;
  background-color: var(--color-coral-50);
}
.nav-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 1.25rem;
  height: 2px;
  background-color: var(--color-coral-500);
  border-radius: 1px;
}
</style>
