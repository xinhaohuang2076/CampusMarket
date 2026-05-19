<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const products = ref([])
const statusFilter = ref('')
const page = ref(1)
const totalPages = ref(0)
const loading = ref(false)

const statusLabels = {
  onsale: { text: '在售', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  reserved: { text: '被预定', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  sold: { text: '已售出', class: 'bg-slate-50 text-slate-500 border-slate-200' },
  removed: { text: '已下架', class: 'bg-coral-50 text-coral-600 border-coral-200' },
}

async function fetchMyProducts() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await api.get('/api/products/mine', { params })
    products.value = data.items
    totalPages.value = data.pages
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

watch(page, fetchMyProducts)
watch(statusFilter, () => { page.value = 1; fetchMyProducts() })

onMounted(fetchMyProducts)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="font-display text-2xl font-bold text-slate-800">我的商品</h1>
        <p class="text-sm text-slate-400 mt-0.5">管理你发布的全部商品</p>
      </div>
      <router-link to="/product/new"
        class="bg-coral-500 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-coral-600 transition btn-press shadow-sm shadow-coral-200">
        + 发布商品
      </router-link>
    </div>

    <div class="flex gap-2 mb-5 flex-wrap">
      <button @click="statusFilter = ''" :class="statusFilter === '' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">全部</button>
      <button @click="statusFilter = 'onsale'" :class="statusFilter === 'onsale' ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-emerald-300'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">在售</button>
      <button @click="statusFilter = 'sold'" :class="statusFilter === 'sold' ? 'bg-slate-500 text-white border-slate-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-slate-300'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">已售</button>
      <button @click="statusFilter = 'removed'" :class="statusFilter === 'removed' ? 'bg-coral-500 text-white border-coral-500 shadow-sm' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
        class="px-4 py-1.5 rounded-xl text-sm font-medium border transition btn-press">已下架</button>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
    </div>
    <div v-else-if="products.length === 0" class="text-center py-16">
      <div class="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      </div>
      <p class="text-slate-400 text-sm">暂无商品</p>
    </div>
    <div v-else class="space-y-3">
      <div v-for="p in products" :key="p.id"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-4 flex items-center gap-4 card-hover cursor-pointer"
        @click="router.push(`/product/${p.id}`)">
        <div class="w-16 h-16 bg-gradient-to-br from-warm-50 to-warm-100 rounded-xl shrink-0 flex items-center justify-center overflow-hidden">
          <img v-if="p.image_urls?.length" :src="p.image_urls[0]" class="w-full h-full object-cover" alt="" />
          <svg v-else class="w-6 h-6 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-medium text-slate-800 truncate">{{ p.title }}</div>
          <div class="text-coral-500 font-bold mt-0.5">¥{{ p.price.toFixed(2) }}</div>
        </div>
        <div class="text-right shrink-0">
          <span :class="statusLabels[p.status]?.class" class="tag border">
            {{ statusLabels[p.status]?.text }}
          </span>
          <div class="text-xs text-slate-300 mt-1.5">{{ p.created_at?.slice(0, 10) }}</div>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="flex items-center justify-center gap-3 mt-8">
      <button @click="page--" :disabled="page <= 1"
        class="px-4 py-2 rounded-xl text-sm font-medium border border-warm-200 text-slate-600 hover:bg-white hover:border-coral-200 hover:text-coral-600 disabled:opacity-30 disabled:cursor-not-allowed transition btn-press">
        上一页
      </button>
      <span class="text-sm font-medium text-slate-500">{{ page }} / {{ totalPages }}</span>
      <button @click="page++" :disabled="page >= totalPages"
        class="px-4 py-2 rounded-xl text-sm font-medium border border-warm-200 text-slate-600 hover:bg-white hover:border-coral-200 hover:text-coral-600 disabled:opacity-30 disabled:cursor-not-allowed transition btn-press">
        下一页
      </button>
    </div>
  </div>
</template>
