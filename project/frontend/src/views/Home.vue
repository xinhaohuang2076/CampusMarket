<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const products = ref([])
const total = ref(0)
const page = ref(1)
const totalPages = ref(0)
const keyword = ref('')
const category = ref('')
const sort = ref('latest')
const loading = ref(false)
const categories = ref([])

const hasFilters = computed(() => keyword.value || category.value)
const filterLabel = computed(() => {
  const parts = []
  if (keyword.value) parts.push(`"${keyword.value}"`)
  if (category.value) parts.push(category.value)
  return parts.join(' · ') || ''
})

watch([keyword, category, sort], () => {
  const parts = ['校园二手交易平台']
  if (keyword.value) parts.unshift(`搜索"${keyword.value}"`)
  document.title = parts.join(' - ')
})

async function fetchProducts() {
  loading.value = true
  try {
    const params = { page: page.value, sort: sort.value }
    if (keyword.value) params.keyword = keyword.value
    if (category.value) params.category = category.value
    const { data } = await api.get('/api/products', { params })
    products.value = data.items
    total.value = data.total
    page.value = data.page
    totalPages.value = data.pages
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const { data } = await api.get('/api/categories')
    categories.value = data.categories
  } catch (e) { console.error(e) }
}

function goDetail(id) {
  router.push(`/product/${id}`)
}

function search() {
  page.value = 1
  fetchProducts()
}

function clearFilters() {
  keyword.value = ''
  category.value = ''
  page.value = 1
  fetchProducts()
}

watch(page, fetchProducts)
watch(category, () => { page.value = 1; fetchProducts() })
watch(sort, () => { page.value = 1; fetchProducts() })

onMounted(() => {
  fetchCategories()
  fetchProducts()
})

function friendlyTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr.replace(' ', 'T') + 'Z')
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  return dateStr.slice(0, 10)
}
</script>

<template>
  <div>
    <!-- 搜索栏 -->
    <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5 mb-8">
      <div class="flex flex-wrap gap-3 items-end">
        <div class="flex-1 min-w-[220px] relative">
          <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input v-model="keyword" @keyup.enter="search"
            class="w-full border border-warm-200 rounded-xl pl-10 pr-3 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
            placeholder="搜索商品名称或描述..." />
        </div>
        <div>
          <select v-model="category"
            class="border border-warm-200 rounded-xl px-3 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy">
            <option value="">全部分类</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div>
          <select v-model="sort"
            class="border border-warm-200 rounded-xl px-3 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy">
            <option value="latest">最新</option>
            <option value="price_asc">价格 ↑</option>
            <option value="price_desc">价格 ↓</option>
          </select>
        </div>
        <button @click="search"
          class="bg-coral-500 text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-coral-600 transition btn-press shadow-sm shadow-coral-200">
          搜索
        </button>
      </div>
    </div>

    <!-- 统计 + 激活的筛选条件 -->
    <div class="flex items-center justify-between mb-5 flex-wrap gap-2">
      <div class="flex items-center gap-2 flex-wrap">
        <p class="text-sm text-slate-400">共 <span class="text-slate-600 font-medium">{{ total }}</span> 件商品</p>
        <span v-if="filterLabel" class="text-sm text-slate-300">·</span>
        <span v-if="filterLabel" class="flex items-center gap-1.5">
          <span class="text-xs tag bg-coral-50 text-coral-600">{{ filterLabel }}</span>
          <button @click="clearFilters"
            class="text-xs text-slate-400 hover:text-coral-500 transition">
            清除
          </button>
        </span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="products.length === 0" class="text-center py-16">
      <div class="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <p class="text-slate-400 text-sm">暂无商品</p>
    </div>

    <!-- 商品网格 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <div v-for="(p, idx) in products" :key="p.id" @click="goDetail(p.id)"
        class="bg-white rounded-2xl card-hover cursor-pointer overflow-hidden border border-warm-100"
        :style="{ animationDelay: `${idx * 40}ms` }">
        <div class="aspect-[4/3] bg-gradient-to-br from-warm-50 to-warm-100 flex items-center justify-center overflow-hidden relative">
          <div class="absolute top-2.5 left-2.5">
            <span v-if="p.condition" class="tag bg-white/80 backdrop-blur-sm text-slate-500 shadow-xs">{{ p.condition }}</span>
          </div>
          <svg v-if="!p.image_urls?.length" class="w-10 h-10 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
          </svg>
          <img v-else :src="p.image_urls[0]" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" alt="" />
        </div>
        <div class="p-3.5">
          <h3 class="text-sm font-semibold text-slate-800 leading-snug line-clamp-2">{{ p.title }}</h3>
          <div class="flex items-baseline gap-1 mt-2">
            <span class="text-lg font-bold text-coral-500">¥</span>
            <span class="text-lg font-bold text-coral-500">{{ p.price.toFixed(2) }}</span>
          </div>
          <div class="flex items-center justify-between mt-2.5 pt-2.5 border-t border-warm-50">
            <span class="text-xs text-slate-400">{{ p.category }}</span>
            <span class="text-[11px] text-slate-300">{{ friendlyTime(p.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-3 mt-10">
      <button @click="page--" :disabled="page <= 1"
        class="px-4 py-2 rounded-xl text-sm font-medium border border-warm-200 text-slate-600 hover:bg-white hover:border-coral-200 hover:text-coral-600 disabled:opacity-30 disabled:cursor-not-allowed transition btn-press">
        上一页
      </button>
      <div class="flex items-center gap-1.5">
        <span class="text-sm font-medium text-slate-500">{{ page }} / {{ totalPages }}</span>
      </div>
      <button @click="page++" :disabled="page >= totalPages"
        class="px-4 py-2 rounded-xl text-sm font-medium border border-warm-200 text-slate-600 hover:bg-white hover:border-coral-200 hover:text-coral-600 disabled:opacity-30 disabled:cursor-not-allowed transition btn-press">
        下一页
      </button>
    </div>
  </div>
</template>
