<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const favorites = ref([])
const loading = ref(false)

async function fetchFavorites() {
  loading.value = true
  try {
    const { data } = await api.get('/api/favorites')
    favorites.value = data.items || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function removeFavorite(productId) {
  try {
    await api.post(`/api/products/${productId}/favorite`)
    favorites.value = favorites.value.filter(f => f.product_id !== productId)
  } catch (e) { console.error(e) }
}

onMounted(fetchFavorites)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="font-display text-2xl font-bold text-slate-800">我的收藏</h1>
      <p class="text-sm text-slate-400 mt-0.5">你收藏的商品</p>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
    </div>
    <div v-else-if="favorites.length === 0" class="text-center py-16">
      <div class="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      </div>
      <p class="text-slate-400 text-sm">还没有收藏的商品</p>
      <router-link to="/" class="inline-block mt-3 text-sm text-coral-500 font-medium hover:text-coral-600">去逛逛</router-link>
    </div>
    <div v-else class="space-y-3">
      <div v-for="fav in favorites" :key="fav.id"
        class="bg-white rounded-2xl shadow-sm border border-warm-100 p-4 flex items-center gap-4 card-hover cursor-pointer"
        @click="fav.product && router.push(`/product/${fav.product_id}`)">
        <div class="w-16 h-16 bg-gradient-to-br from-warm-50 to-warm-100 rounded-xl shrink-0 flex items-center justify-center overflow-hidden">
          <img v-if="fav.product?.image_urls?.length" :src="fav.product.image_urls[0]" class="w-full h-full object-cover" alt="" />
          <svg v-else class="w-6 h-6 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-medium text-slate-800 truncate">{{ fav.product?.title || '商品已下架' }}</div>
          <div v-if="fav.product" class="text-coral-500 font-bold mt-0.5">¥{{ fav.product.price.toFixed(2) }}</div>
        </div>
        <button @click.stop="removeFavorite(fav.product_id)"
          class="text-sm text-slate-400 hover:text-coral-500 transition p-2 rounded-xl hover:bg-coral-50 shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
