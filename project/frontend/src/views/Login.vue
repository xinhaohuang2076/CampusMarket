<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const form = reactive({ student_id: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  if (!form.student_id || !form.password) {
    error.value = '请填写学号和密码'
    return
  }
  loading.value = true
  try {
    const { data } = await api.post('/api/auth/login', form)
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    window.dispatchEvent(new Event('user-changed'))
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.error || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[70vh] flex items-center justify-center">
    <div class="w-full max-w-sm">
      <!-- 头部 -->
      <div class="text-center mb-8">
        <div class="w-14 h-14 bg-coral-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-coral-200">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </div>
        <h1 class="font-display text-2xl font-bold text-slate-800">欢迎回来</h1>
        <p class="text-sm text-slate-400 mt-1">登录你的 CampusMarket 账号</p>
      </div>

      <!-- 表单 -->
      <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6">
        <div v-if="error" class="bg-coral-50 border border-coral-100 text-coral-700 text-sm rounded-xl p-3 mb-5">{{ error }}</div>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">学号</label>
            <input v-model="form.student_id" type="text" data-testid="login-student-id"
              class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="10位学号" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">密码</label>
            <input v-model="form.password" type="password" data-testid="login-password"
              class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="输入密码" />
          </div>
          <button type="submit" data-testid="login-submit" :disabled="loading"
            class="w-full bg-coral-500 text-white py-2.5 rounded-xl font-medium hover:bg-coral-600 disabled:opacity-50 transition btn-press shadow-sm shadow-coral-200">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
        <p class="text-xs text-center text-slate-400 mt-5">
          还没有账号？<router-link to="/register" class="text-coral-500 font-medium hover:text-coral-600">注册</router-link>
        </p>
      </div>

      <!-- 测试提示 -->
      <div class="mt-4 text-center">
        <p class="text-[11px] text-slate-300">测试账号：2202300001 ~ 2202300005，密码 123456</p>
      </div>
    </div>
  </div>
</template>
