<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import Modal from '../components/Modal.vue'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const form = ref({ ...user.value })
const loading = ref(false)
const message = ref('')
const error = ref('')
const pwForm = ref({ old_password: '', new_password: '', confirm: '' })
const pwLoading = ref(false)
const pwMsg = ref('')
const pwError = ref('')
const showModal = ref(false)
const modalMsg = ref('')

async function updateProfile() {
  error.value = ''
  message.value = ''
  loading.value = true
  try {
    const { data } = await api.put('/api/user/profile', {
      nickname: form.value.nickname,
      email: form.value.email,
      phone: form.value.phone,
    })
    localStorage.setItem('user', JSON.stringify(data.user))
    user.value = data.user
    message.value = '更新成功'
  } catch (e) {
    error.value = e.response?.data?.error || '更新失败'
  } finally {
    loading.value = false
  }
}

async function changePassword() {
  pwError.value = ''
  pwMsg.value = ''
  if (!pwForm.value.old_password || !pwForm.value.new_password) {
    pwError.value = '请填写旧密码和新密码'
    return
  }
  if (pwForm.value.new_password.length < 6) {
    pwError.value = '新密码至少6位'
    return
  }
  if (pwForm.value.new_password !== pwForm.value.confirm) {
    pwError.value = '两次输入的新密码不一致'
    return
  }
  pwLoading.value = true
  try {
    const { data } = await api.put('/api/user/password', {
      old_password: pwForm.value.old_password,
      new_password: pwForm.value.new_password,
    })
    pwMsg.value = data.message
    pwForm.value = { old_password: '', new_password: '', confirm: '' }
  } catch (e) {
    pwError.value = e.response?.data?.error || '修改失败'
  } finally {
    pwLoading.value = false
  }
}

const productCount = ref(0)
const favoriteCount = ref(0)
const transactionCount = ref(0)

async function fetchStats() {
  try {
    const [p, f, t] = await Promise.all([
      api.get('/api/products/mine', { params: { page: 1 } }),
      api.get('/api/favorites'),
      api.get('/api/transactions', { params: { role: 'all' } }),
    ])
    productCount.value = p.data.total || 0
    favoriteCount.value = f.data.total || f.data.items?.length || 0
    transactionCount.value = t.data.total || t.data.items?.length || 0
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/user/profile')
    form.value = { ...data.user }
  } catch (e) { console.error(e) }
  fetchStats()
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-8 text-center mb-6">
      <div class="w-20 h-20 bg-gradient-to-br from-coral-400 to-coral-500 rounded-full flex items-center justify-center mx-auto shadow-lg shadow-coral-200">
        <span class="text-2xl font-bold text-white">{{ (form.nickname || form.student_id || '?')[0] }}</span>
      </div>
      <h1 class="font-display text-xl font-bold text-slate-800 mt-4">{{ form.nickname }}</h1>
      <div class="text-sm text-slate-400 mt-1">学号 {{ form.student_id }}</div>
      <div class="inline-flex items-center gap-1.5 mt-3 tag bg-coral-50 text-coral-600">
        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        信用分 {{ form.credit || user.credit }}
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6 mb-6">
      <div v-if="message" class="bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm rounded-xl p-3 mb-5">{{ message }}</div>
      <div v-if="error" class="bg-coral-50 border border-coral-100 text-coral-700 text-sm rounded-xl p-3 mb-5">{{ error }}</div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">昵称</label>
          <input v-model="form.nickname" type="text"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">邮箱</label>
          <input v-model="form.email" type="text"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">手机号</label>
          <input v-model="form.phone" type="text"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
            placeholder="选填" />
        </div>
        <button @click="updateProfile" :disabled="loading"
          class="w-full bg-coral-500 text-white py-2.5 rounded-xl font-medium hover:bg-coral-600 disabled:opacity-50 transition btn-press shadow-sm shadow-coral-200">
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6 mb-6">
      <h3 class="font-display font-bold text-slate-800 mb-4">修改密码</h3>
      <div v-if="pwMsg" class="bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm rounded-xl p-3 mb-4">{{ pwMsg }}</div>
      <div v-if="pwError" class="bg-coral-50 border border-coral-100 text-coral-700 text-sm rounded-xl p-3 mb-4">{{ pwError }}</div>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">旧密码</label>
          <input v-model="pwForm.old_password" type="password"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">新密码</label>
          <input v-model="pwForm.new_password" type="password"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
            placeholder="至少6位" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">确认新密码</label>
          <input v-model="pwForm.confirm" type="password"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy" />
        </div>
        <button @click="changePassword" :disabled="pwLoading"
          class="w-full border-2 border-coral-200 text-coral-600 py-2.5 rounded-xl font-medium hover:bg-coral-50 disabled:opacity-50 transition btn-press">
          {{ pwLoading ? '修改中...' : '修改密码' }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-4 gap-3">
      <router-link to="/my-products"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-4 text-center hover:border-coral-200 hover:shadow-md transition card-hover">
        <div class="text-lg font-bold text-coral-500">{{ productCount }}</div>
        <div class="text-xs text-slate-500 mt-1">商品</div>
      </router-link>
      <router-link to="/favorites"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-4 text-center hover:border-coral-200 hover:shadow-md transition card-hover">
        <div class="text-lg font-bold text-coral-500">{{ favoriteCount }}</div>
        <div class="text-xs text-slate-500 mt-1">收藏</div>
      </router-link>
      <router-link to="/transactions"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-4 text-center hover:border-coral-200 hover:shadow-md transition card-hover">
        <div class="text-lg font-bold text-coral-500">{{ transactionCount }}</div>
        <div class="text-xs text-slate-500 mt-1">交易</div>
      </router-link>
      <router-link to="/messages"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-4 text-center hover:border-coral-200 hover:shadow-md transition card-hover">
        <div class="w-10 h-10 bg-coral-50 rounded-xl flex items-center justify-center mx-auto mb-1">
          <svg class="w-5 h-5 text-coral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951" />
          </svg>
        </div>
        <div class="text-xs text-slate-500">留言</div>
      </router-link>
    </div>
  </div>
</template>
