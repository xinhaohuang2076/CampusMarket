<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const messages = ref([])
const direction = ref('received')
const loading = ref(false)
const replyingTo = ref(null)
const replyContent = ref('')

async function fetchMessages() {
  loading.value = true
  try {
    const { data } = await api.get('/api/messages/mine', { params: { direction: direction.value } })
    messages.value = data.items || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function startReply(msg) {
  replyingTo.value = msg.id
  replyContent.value = ''
}

function cancelReply() {
  replyingTo.value = null
  replyContent.value = ''
}

async function submitReply(msg) {
  if (!replyContent.value.trim()) return
  try {
    await api.post(`/api/products/${msg.product_id}/messages`, {
      content: replyContent.value.trim(),
      parent_id: msg.id
    })
    replyContent.value = ''
    replyingTo.value = null
    fetchMessages()
  } catch (e) { console.error(e) }
}

watch(direction, fetchMessages)
onMounted(fetchMessages)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="font-display text-2xl font-bold text-slate-800">我的留言</h1>
      <p class="text-sm text-slate-400 mt-0.5">查看和回复所有留言</p>
    </div>

    <div class="flex gap-2 mb-5">
      <button @click="direction = 'received'"
        :class="direction === 'received' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">
        我收到的
      </button>
      <button @click="direction = 'sent'"
        :class="direction === 'sent' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">
        我发出的
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
    </div>
    <div v-else-if="messages.length === 0" class="text-center py-16">
      <div class="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
        </svg>
      </div>
      <p class="text-slate-400 text-sm">{{ direction === 'received' ? '还没有收到留言' : '还没有发出留言' }}</p>
    </div>
    <div v-else class="space-y-3">
      <div v-for="msg in messages" :key="msg.id"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5 card-hover cursor-pointer"
        @click="router.push(`/product/${msg.product_id}`)">
        <div class="flex gap-3">
          <div class="w-10 h-10 bg-coral-100 text-coral-600 rounded-full flex items-center justify-center text-sm font-semibold shrink-0">
            {{ msg.from_nickname?.[0] }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-medium text-slate-700 text-sm">{{ msg.from_nickname }}</span>
              <svg class="w-3 h-3 text-slate-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
              <span class="font-medium text-slate-700 text-sm">{{ msg.to_nickname }}</span>
              <span class="text-xs text-slate-300 ml-auto">{{ msg.created_at }}</span>
            </div>
            <p class="text-sm text-slate-600 mt-1.5">{{ msg.content }}</p>

            <!-- 回复按钮（只能回复收到的留言） -->
            <div v-if="direction === 'received' && replyingTo !== msg.id" class="mt-2">
              <button @click.stop="startReply(msg)"
                class="text-xs text-slate-400 hover:text-coral-500 transition">
                回复
              </button>
            </div>

            <!-- 回复输入框 -->
            <div v-if="replyingTo === msg.id" @click.stop
              class="mt-3 flex gap-2">
              <input v-model="replyContent" @keyup.enter="submitReply(msg)" type="text"
                class="flex-1 border border-warm-200 rounded-lg px-3 py-1.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
                placeholder="回复..." />
              <button @click="submitReply(msg)"
                class="text-sm bg-coral-500 text-white px-3.5 py-1.5 rounded-lg hover:bg-coral-600 transition btn-press">
                发送
              </button>
              <button @click="cancelReply"
                class="text-sm text-slate-400 px-2 hover:text-slate-600 transition">
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
