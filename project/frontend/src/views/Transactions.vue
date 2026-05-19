<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import Modal from '../components/Modal.vue'

const router = useRouter()
const transactions = ref([])
const roleFilter = ref('all')
const loading = ref(false)
const currentUser = ref(JSON.parse(localStorage.getItem('user') || '{}'))

const reviewedTids = ref(new Set())
const reviewing = ref(null)
const reviewForm = ref({ rating: 0, content: '' })
const submitting = ref(false)
const showModal = ref(false)
const modalMsg = ref('')
const modalType = ref('confirm')
const modalVariant = ref('primary')
const pendingAction = ref(null)

const statusLabels = {
  pending: { text: '待确认', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  completed: { text: '已完成', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  cancelled: { text: '已取消', class: 'bg-slate-50 text-slate-500 border-slate-200' },
}

async function fetchTransactions() {
  loading.value = true
  try {
    const { data } = await api.get('/api/transactions', { params: { role: roleFilter.value } })
    transactions.value = data.items || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function confirmComplete(tid) {
  modalMsg.value = '确认完成此交易？'
  modalType.value = 'confirm'
  modalVariant.value = 'primary'
  pendingAction.value = { action: 'complete', tid }
  showModal.value = true
}

function confirmCancel(tid) {
  modalMsg.value = '确定取消此交易？'
  modalType.value = 'confirm'
  modalVariant.value = 'danger'
  pendingAction.value = { action: 'cancel', tid }
  showModal.value = true
}

async function doAction() {
  if (!pendingAction.value) return
  const { action, tid } = pendingAction.value
  pendingAction.value = null
  try {
    await api.put(`/api/transactions/${tid}`, { action })
    fetchTransactions()
  } catch (e) {
    modalMsg.value = e.response?.data?.error || '操作失败'
    modalType.value = 'alert'
    showModal.value = true
  }
}

function startReview(t) {
  reviewing.value = t.id
  reviewForm.value = { rating: 0, content: '' }
}

function cancelReview() {
  reviewing.value = null
  reviewForm.value = { rating: 0, content: '' }
}

async function submitReview() {
  if (reviewForm.value.rating === 0) {
    modalMsg.value = '请先选择评分'
    modalType.value = 'alert'
    showModal.value = true
    return
  }
  submitting.value = true
  try {
    await api.post('/api/reviews', {
      transaction_id: reviewing.value,
      rating: reviewForm.value.rating,
      content: reviewForm.value.content.trim()
    })
    reviewedTids.value.add(reviewing.value)
    cancelReview()
    fetchTransactions()
  } catch (e) {
    if (e.response?.status === 409) {
      reviewedTids.value.add(reviewing.value)
      cancelReview()
    } else {
      modalMsg.value = e.response?.data?.error || '评价提交失败'
      modalType.value = 'alert'
      showModal.value = true
    }
  } finally {
    submitting.value = false
  }
}

const hoverStar = ref(0)

watch(roleFilter, fetchTransactions)
onMounted(fetchTransactions)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="font-display text-2xl font-bold text-slate-800">交易记录</h1>
      <p class="text-sm text-slate-400 mt-0.5">查看你所有的买卖记录</p>
    </div>

    <div class="flex gap-2 mb-5 flex-wrap">
      <button @click="roleFilter = 'all'" :class="roleFilter === 'all' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">全部</button>
      <button @click="roleFilter = 'buy'" :class="roleFilter === 'buy' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">我买到的</button>
      <button @click="roleFilter = 'sell'" :class="roleFilter === 'sell' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">我卖出的</button>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
    </div>
    <div v-else-if="transactions.length === 0" class="text-center py-16">
      <div class="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
        </svg>
      </div>
      <p class="text-slate-400 text-sm">暂无交易记录</p>
    </div>
    <div v-else class="space-y-3">
      <div v-for="t in transactions" :key="t.id"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5 card-hover">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4 min-w-0">
            <div class="w-10 h-10 bg-coral-50 rounded-xl flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-coral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m6 4.125l2.25 2.25m0 0l2.25-2.25M12 13.875V7.5" />
              </svg>
            </div>
            <div class="min-w-0">
              <div class="font-medium text-slate-800 truncate">{{ t.product_title || '商品' }}</div>
              <div class="text-xs text-slate-400 mt-0.5">
                <template v-if="t.seller_id === (currentUser.id)">
                  买家：{{ t.buyer_nickname }}
                </template>
                <template v-else>
                  卖家：{{ t.seller_nickname }}
                </template>
              </div>
            </div>
          </div>
          <div class="text-right shrink-0 min-w-[90px]">
            <span :class="statusLabels[t.status]?.class" class="tag border">
              {{ statusLabels[t.status]?.text }}
            </span>
            <div class="text-xs text-slate-300 mt-1.5">{{ t.created_at?.slice(0, 10) }}</div>

            <div v-if="t.status === 'pending' && t.seller_id === currentUser.id" class="flex gap-1.5 mt-2 justify-end">
              <button @click.stop="confirmComplete(t.id)"
                class="text-xs bg-emerald-500 text-white px-2.5 py-1 rounded-lg hover:bg-emerald-600 transition font-medium">确认</button>
              <button @click.stop="confirmCancel(t.id)"
                class="text-xs border border-slate-200 text-slate-500 px-2.5 py-1 rounded-lg hover:border-coral-200 hover:text-coral-500 transition">取消</button>
            </div>

            <div v-else-if="t.status === 'completed' && t.buyer_id === currentUser.id" class="mt-2">
              <button v-if="!reviewedTids.has(t.id) && reviewing !== t.id"
                @click.stop="startReview(t)"
                class="text-xs bg-coral-500 text-white px-3 py-1 rounded-lg hover:bg-coral-600 transition font-medium">
                评价卖家
              </button>
              <span v-else-if="reviewedTids.has(t.id)" class="text-xs text-emerald-600 font-medium">已评价</span>
            </div>
          </div>
        </div>

        <div v-if="reviewing === t.id" class="mt-4 pt-4 border-t border-warm-100" @click.stop>
          <p class="text-sm font-medium text-slate-700 mb-2">评价卖家 {{ t.seller_nickname }}</p>
          <div class="flex items-center gap-1 mb-3">
            <span v-for="s in 5" :key="s" @click="reviewForm.rating = s"
              @mouseenter="hoverStar = s" @mouseleave="hoverStar = 0"
              class="text-2xl cursor-pointer transition select-none"
              :class="s <= (hoverStar || reviewForm.rating) ? 'text-amber-400' : 'text-slate-200'">
              ★
            </span>
            <span class="text-xs text-slate-400 ml-2">
              {{ ['', '很差', '较差', '一般', '满意', '非常满意'][reviewForm.rating] || '' }}
            </span>
          </div>
          <textarea v-model="reviewForm.content" rows="2" maxlength="500"
            class="w-full border border-warm-200 rounded-xl px-3 py-2 text-sm bg-warm-50 focus:bg-white transition input-fancy resize-none mb-2"
            placeholder="写写你的交易体验（选填）"></textarea>
          <div class="flex gap-2 justify-end">
            <button @click="cancelReview"
              class="text-xs border border-slate-200 text-slate-500 px-3 py-1.5 rounded-lg hover:border-coral-200 transition">
              取消
            </button>
            <button @click="submitReview" :disabled="submitting"
              class="text-xs bg-coral-500 text-white px-4 py-1.5 rounded-lg hover:bg-coral-600 disabled:opacity-50 transition font-medium">
              {{ submitting ? '提交中...' : '提交评价' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <Modal :show="showModal" :title="modalType === 'confirm' ? '确认操作' : ''"
      :message="modalMsg" :type="modalType" :variant="modalVariant"
      confirmText="确定" cancelText="取消"
      @update:show="showModal = $event" @confirm="doAction" @cancel="pendingAction = null" />
  </div>
</template>
