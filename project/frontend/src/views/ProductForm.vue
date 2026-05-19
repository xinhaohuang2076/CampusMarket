<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id && route.params.id !== 'new')
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const categories = ref([])
const conditions = ref([])

const form = reactive({
  title: '',
  description: '',
  price: '',
  category: '其他',
  condition: '九成新',
  image_urls: [],
})

const uploading = ref(false)

async function handleUpload(e) {
  const files = e.target.files
  if (!files?.length) return
  const file = files[0]
  if (file.size > 16 * 1024 * 1024) {
    error.value = '图片不能超过 16MB'
    return
  }
  uploading.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/api/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.image_urls.push(data.url)
  } catch (e) {
    error.value = e.response?.data?.error || '上传失败'
  } finally {
    uploading.value = false
  }
}

function removeImage(idx) {
  form.image_urls.splice(idx, 1)
}

async function fetchCategories() {
  try {
    const [{ data: catData }, { data: conData }] = await Promise.all([
      api.get('/api/categories'),
      api.get('/api/conditions'),
    ])
    categories.value = catData.categories
    conditions.value = conData.conditions
  } catch (e) { console.error(e) }
}

async function fetchProduct() {
  if (!isEdit.value) return
  loading.value = true
  try {
    const { data } = await api.get(`/api/products/${route.params.id}`)
    const p = data.product
    form.title = p.title
    form.description = p.description
    form.price = String(p.price)
    form.category = p.category
    form.condition = p.condition
    form.image_urls = p.image_urls || []
  } catch (e) {
    error.value = '商品不存在'
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  error.value = ''
  if (!form.title.trim()) { error.value = '请输入商品标题'; return }
  if (!form.price || isNaN(form.price) || parseFloat(form.price) < 0) { error.value = '请输入有效价格'; return }

  submitting.value = true
  try {
    const payload = { ...form, price: parseFloat(form.price) }
    if (isEdit.value) {
      await api.put(`/api/products/${route.params.id}`, payload)
      router.push(`/product/${route.params.id}`)
    } else {
      const { data } = await api.post('/api/products', payload)
      router.push(`/product/${data.product.id}`)
    }
  } catch (e) {
    error.value = e.response?.data?.error || '提交失败'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCategories()
  if (isEdit.value) fetchProduct()
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="text-center mb-8">
      <h1 class="font-display text-2xl font-bold text-slate-800">{{ isEdit ? '编辑商品' : '发布商品' }}</h1>
      <p class="text-sm text-slate-400 mt-1">{{ isEdit ? '修改商品信息' : '分享你的闲置物品给同学们' }}</p>
    </div>

    <div v-if="error" class="bg-coral-50 border border-coral-100 text-coral-700 text-sm rounded-xl p-4 mb-5">{{ error }}</div>
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-3 border-coral-200 border-t-coral-500 rounded-full animate-spin"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="bg-white rounded-2xl shadow-sm border border-warm-100 p-6 space-y-5">
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5">标题 <span class="text-coral-400">*</span></label>
        <input v-model="form.title" type="text" maxlength="100"
          class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
          placeholder="商品名称" />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">价格 <span class="text-coral-400">*</span></label>
          <div class="relative">
            <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm">¥</span>
            <input v-model="form.price" type="number" step="0.01" min="0"
              class="w-full border border-warm-200 rounded-xl pl-8 pr-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy"
              placeholder="0.00" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">分类</label>
          <select v-model="form.category"
            class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy">
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5">成色</label>
        <div class="flex flex-wrap gap-2">
          <button v-for="c in conditions" :key="c" type="button" @click="form.condition = c"
            :class="form.condition === c ? 'bg-coral-500 text-white border-coral-500 shadow-sm shadow-coral-200' : 'bg-white text-slate-600 border-warm-200 hover:border-coral-200'"
            class="px-3.5 py-2 rounded-xl text-sm border transition btn-press">
            {{ c }}
          </button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5">图片</label>
        <div class="flex flex-wrap gap-3">
          <div v-for="(url, idx) in form.image_urls" :key="idx"
            class="relative w-24 h-24 rounded-xl overflow-hidden bg-warm-50 border border-warm-200 group">
            <img :src="url" class="w-full h-full object-cover" alt="" />
            <button type="button" @click="removeImage(idx)"
              class="absolute top-1 right-1 w-5 h-5 bg-black/40 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
              ✕
            </button>
          </div>
          <label v-if="form.image_urls.length < 6"
            class="w-24 h-24 border-2 border-dashed border-warm-200 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:border-coral-300 hover:bg-coral-50 transition text-slate-400 hover:text-coral-500">
            <input type="file" accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              @change="handleUpload" class="hidden" />
            <svg v-if="!uploading" class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            <div v-else class="w-5 h-5 border-2 border-coral-300 border-t-coral-500 rounded-full animate-spin mb-1"></div>
            <span class="text-[11px]">{{ uploading ? '上传中' : '添加图片' }}</span>
          </label>
        </div>
        <p class="text-xs text-slate-400 mt-1.5">支持 jpg/png/gif/webp，最多 6 张，每张不超过 16MB</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5">描述</label>
        <textarea v-model="form.description" rows="4"
          class="w-full border border-warm-200 rounded-xl px-3.5 py-2.5 text-sm bg-warm-50 focus:bg-white transition input-fancy resize-none"
          placeholder="商品描述、使用情况、交易方式等"></textarea>
      </div>

      <div class="pt-2">
        <button type="submit" :disabled="submitting"
          class="w-full bg-coral-500 text-white py-2.5 rounded-xl font-medium hover:bg-coral-600 disabled:opacity-50 transition btn-press shadow-sm shadow-coral-200">
          {{ submitting ? '提交中...' : (isEdit ? '保存修改' : '发布商品') }}
        </button>
      </div>
    </form>
  </div>
</template>
