<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const form = reactive({ student_id: '', email: '', password: '', nickname: '' })
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  if (!form.student_id || !form.email || !form.password) {
    error.value = '请填写所有必填项'
    return
  }
  if (form.student_id.length !== 10) {
    error.value = '学号必须为10位'
    return
  }
  loading.value = true
  try {
    const { data } = await api.post('/api/auth/register', form)
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    window.dispatchEvent(new Event('user-changed'))
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.error || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[70vh] flex items-center justify-center">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="w-14 h-14 bg-coral-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-coral-200">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
          </svg>
        </div>
        <h1 class="font-display text-2xl font-bold text-slate-800">加入我们</h1>
        <p class="text-sm text-slate-400 mt-1">创建你的 CampusMarket 账号</p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6">
        <div v-if="error" class="bg-coral-50 border border-coral-100 text-coral-700 text-sm rounded-xl p-3 mb-5">{{ error }}</div>
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">学号 <span class="text-coral-400">*</span></label>
            <input v-model="form.student_id" type="text" maxlength="10"
              class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="22023开头，10位数字" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">邮箱 <span class="text-coral-400">*</span></label>
            <input v-model="form.email" type="text"
              class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="@qq.com 或 @163.com" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">密码 <span class="text-coral-400">*</span></label>
            <input v-model="form.password" type="password"
              class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="6-64位密码" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">昵称</label>
            <input v-model="form.nickname" type="text"
              class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="选填，默认使用学号" />
          </div>
          <button type="submit" :disabled="loading"
            class="w-full bg-coral-500 text-white py-2.5 rounded-xl font-medium hover:bg-coral-600 disabled:opacity-50 transition btn-press shadow-sm shadow-coral-200">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
        <p class="text-xs text-center text-slate-400 mt-5">
          已有账号？<router-link to="/login" class="text-coral-500 font-medium hover:text-coral-600">登录</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
