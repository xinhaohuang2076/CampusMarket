<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import Modal from '../components/Modal.vue'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const messages = ref([])
const newMessage = ref('')
const replyContent = ref('')
const replyingTo = ref(null)
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
const loading = ref(true)
const favorited = ref(false)
const error = ref('')
const showModal = ref(false)
const modalMsg = ref('')
const modalType = ref('confirm')
const modalVariant = ref('primary')
const pendingAction = ref(null)

const isOwner = computed(() => user.value && product.value?.user_id === user.value.id)

const statusConfig = {
  onsale: { text: '在售', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  reserved: { text: '已被预定', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  sold: { text: '已售出', class: 'bg-slate-50 text-slate-500 border-slate-200' },
  removed: { text: '已下架', class: 'bg-coral-50 text-coral-600 border-coral-200' },
}

async function fetchProduct() {
  try {
    const { data } = await api.get(`/api/products/${route.params.id}`)
    product.value = data.product
  } catch (e) {
    error.value = '商品不存在或已下架'
  } finally {
    loading.value = false
  }
}

async function fetchMessages() {
  try {
    const { data } = await api.get(`/api/products/${route.params.id}/messages`)
    messages.value = data.items
  } catch (e) { console.error(e) }
}

async function toggleFavorite() {
  if (!user.value) { router.push('/login'); return }
  try {
    const { data } = await api.post(`/api/products/${route.params.id}/favorite`)
    favorited.value = data.favorited
  } catch (e) { console.error(e) }
}

async function checkFavorite() {
  try {
    const { data } = await api.get('/api/favorites')
    favorited.value = data.items.some(f => f.product_id === parseInt(route.params.id))
  } catch (e) { console.error(e) }
}

async function sendMessage() {
  if (!user.value) { router.push('/login'); return }
  if (!newMessage.value.trim()) return
  try {
    await api.post(`/api/products/${route.params.id}/messages`, { content: newMessage.value.trim() })
    newMessage.value = ''
    fetchMessages()
  } catch (e) { console.error(e) }
}

function startReply(msg) {
  replyingTo.value = msg
  replyContent.value = ''
}

async function submitReply() {
  if (!replyContent.value.trim()) return
  try {
    await api.post(`/api/products/${route.params.id}/messages`, {
      content: replyContent.value.trim(),
      parent_id: replyingTo.value.id
    })
    replyContent.value = ''
    replyingTo.value = null
    fetchMessages()
  } catch (e) { console.error(e) }
}

function confirmRemove() {
  modalMsg.value = '确定下架此商品？下架后不可恢复。'
  modalType.value = 'confirm'
  modalVariant.value = 'danger'
  pendingAction.value = 'remove'
  showModal.value = true
}

async function doRemove() {
  try {
    await api.delete(`/api/products/${product.value.id}`)
    router.push('/my-products')
  } catch (e) {
    modalMsg.value = e.response?.data?.error || '操作失败'
    modalType.value = 'alert'
    modalVariant.value = 'primary'
    showModal.value = true
  }
}

async function initiateTransaction() {
  if (!user.value) { router.push('/login'); return }
  try {
    await api.post('/api/transactions', { product_id: product.value.id })
    modalMsg.value = '交易意向已发送，等待卖家确认'
    modalType.value = 'alert'
    modalVariant.value = 'primary'
    pendingAction.value = null
    showModal.value = true
  } catch (e) {
    modalMsg.value = e.response?.data?.error || '操作失败'
    modalType.value = 'alert'
    showModal.value = true
  }
}

function onModalConfirm() {
  if (pendingAction.value === 'remove') doRemove()
}

onMounted(() => {
  fetchProduct()
  fetchMessages()
  if (user.value) checkFavorite()
})
</script>

<template>
  <div v-if="loading" class="flex justify-center py-24">
    <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
  </div>
  <div v-else-if="error" class="text-center py-24">
    <div class="w-16 h-16 bg-coral-50 rounded-full flex items-center justify-center mx-auto mb-4">
      <svg class="w-8 h-8 text-coral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
    </div>
    <p class="text-slate-400 text-sm">{{ error }}</p>
  </div>

  <div v-else-if="product" class="max-w-5xl mx-auto">
    <div class="flex items-center gap-2 text-xs text-slate-400 mb-6">
      <router-link to="/" class="hover:text-coral-500 transition">首页</router-link>
      <span>/</span>
      <span class="text-slate-600">{{ product.title }}</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
      <div class="md:col-span-3">
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 overflow-hidden">
          <div class="aspect-square bg-gradient-to-br from-warm-50 to-warm-100 flex items-center justify-center">
            <img v-if="product.image_urls?.length" :src="product.image_urls[0]" class="w-full h-full object-cover" alt="" />
            <svg v-else class="w-24 h-24 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="md:col-span-2">
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6 sticky top-24">
          <div class="flex items-start justify-between gap-3">
            <h1 class="font-display text-xl font-bold text-slate-800 leading-snug" data-testid="product-title">{{ product.title }}</h1>
            <span :class="statusConfig[product.status]?.class" class="tag border shrink-0">
              {{ statusConfig[product.status]?.text }}
            </span>
          </div>

          <div class="mt-4 flex items-baseline gap-1">
            <span class="text-2xl font-bold text-coral-500">¥</span>
            <span class="text-3xl font-bold text-coral-500" data-testid="product-price">{{ product.price.toFixed(2) }}</span>
          </div>

          <div class="flex flex-wrap gap-2 mt-4">
            <span class="tag bg-warm-100 text-slate-600">{{ product.category }}</span>
            <span v-if="product.condition" class="tag bg-warm-100 text-slate-600">{{ product.condition }}</span>
          </div>

          <p class="text-sm text-slate-600 mt-4 whitespace-pre-wrap leading-relaxed">{{ product.description || '暂无描述' }}</p>

          <div class="flex items-center gap-3 mt-5 p-3.5 bg-warm-50 rounded-xl">
            <div class="w-10 h-10 bg-coral-100 text-coral-600 rounded-full flex items-center justify-center text-sm font-semibold shrink-0">
              {{ (product.seller_nickname || '?')[0] }}
            </div>
            <div class="text-sm">
              <div class="font-medium text-slate-700">{{ product.seller_nickname }}</div>
              <div class="text-xs text-slate-400">信用分 {{ product.seller_credit }}</div>
            </div>
          </div>

          <div class="text-xs text-slate-400 mt-4 space-y-1">
            <div>发布时间：{{ product.created_at }}</div>
            <div>浏览 {{ product.view_count }} 次</div>
          </div>

          <div class="flex flex-wrap gap-2.5 mt-6 pt-5 border-t border-warm-100">
            <template v-if="isOwner">
              <router-link :to="`/product/${product.id}/edit`"
                class="flex-1 text-center border-2 border-coral-200 text-coral-600 px-4 py-2.5 rounded-xl font-medium text-sm hover:bg-coral-50 transition btn-press">
                编辑商品
              </router-link>
              <button @click="confirmRemove"
                class="flex-1 border-2 border-slate-200 text-slate-500 px-4 py-2.5 rounded-xl font-medium text-sm hover:border-coral-200 hover:text-coral-500 transition btn-press">
                下架
              </button>
            </template>
            <template v-else-if="product.status === 'onsale' || product.status === 'reserved'">
              <button @click="initiateTransaction" data-testid="want-btn"
                class="flex-1 bg-coral-500 text-white px-6 py-2.5 rounded-xl font-medium text-sm hover:bg-coral-600 transition btn-press shadow-sm shadow-coral-200">
                我想要
              </button>
              <button @click="toggleFavorite" data-testid="favorite-btn"
                :class="favorited ? 'bg-coral-50 border-coral-200 text-coral-500' : 'border-slate-200 text-slate-500 hover:border-coral-200 hover:text-coral-500'"
                class="border-2 px-4 py-2.5 rounded-xl font-medium text-sm transition btn-press">
                <span v-if="favorited">♥</span>
                <span v-else>♡</span>
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6 mt-6">
      <h3 class="font-display font-bold text-lg text-slate-800 mb-5">留言 <span class="text-slate-300 font-normal text-sm">({{ messages.length }})</span></h3>

      <div v-if="user && !isOwner && product.status !== 'removed'" class="flex gap-2.5 mb-6">
        <input v-model="newMessage" @keyup.enter="sendMessage" type="text" data-testid="message-input"
          class="flex-1 border border-warm-200 rounded-xl px-4 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
          placeholder="咨询卖家..." />
        <button @click="sendMessage" :disabled="!newMessage.trim()" data-testid="send-msg-btn"
          class="bg-coral-500 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-coral-600 disabled:opacity-50 transition btn-press">
          发送
        </button>
      </div>

      <div v-if="messages.length === 0" class="text-center py-8">
        <p class="text-xs text-slate-400">暂无留言，来问问卖家吧</p>
      </div>

      <div v-for="msg in messages" :key="msg.id" class="border-b border-warm-100 last:border-0 py-4">
        <div class="flex gap-3">
          <div class="w-8 h-8 bg-coral-100 text-coral-600 rounded-full flex items-center justify-center text-xs font-semibold shrink-0 mt-0.5">
            {{ msg.from_nickname?.[0] }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-slate-700">{{ msg.from_nickname }}</span>
              <span class="text-[11px] text-slate-300">{{ msg.created_at }}</span>
            </div>
            <p class="text-sm text-slate-600 mt-1">{{ msg.content }}</p>
            <button v-if="user && product.status !== 'removed'" @click="startReply(msg)"
              class="text-xs text-slate-400 hover:text-coral-500 mt-1.5 transition">回复</button>

            <div v-if="replyingTo?.id === msg.id" class="flex gap-2 mt-2">
              <input v-model="replyContent" @keyup.enter="submitReply" type="text"
                class="flex-1 border border-warm-200 rounded-lg px-3 py-1.5 text-xs bg-warm-50 focus:bg-white transition input-fancy"
                placeholder="回复..." />
              <button @click="submitReply" class="text-xs bg-coral-500 text-white px-3 rounded-lg hover:bg-coral-600 transition">发送</button>
              <button @click="replyingTo = null" class="text-xs text-slate-400 px-2">取消</button>
            </div>

            <div v-for="reply in msg.replies" :key="reply.id" class="ml-3 mt-3 pl-3.5 border-l-2 border-coral-200">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-coral-600">{{ reply.from_nickname }}</span>
                <span class="text-[11px] text-slate-300">{{ reply.created_at }}</span>
              </div>
              <p class="text-sm text-slate-600 mt-0.5">{{ reply.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Modal :show="showModal" :title="modalType === 'confirm' ? '确认操作' : ''"
      :message="modalMsg" :type="modalType" :variant="modalVariant"
      confirmText="确定" cancelText="取消"
      @update:show="showModal = $event" @confirm="onModalConfirm" @cancel="pendingAction = null" />
  </div>
</template>
