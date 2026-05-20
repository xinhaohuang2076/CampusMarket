<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/index.js'
import Modal from '../components/Modal.vue'

const router = useRouter()
const activeTab = ref('dashboard')

// --- Modal ---
const modal = ref({ show: false, title: '', message: '', type: 'confirm', variant: 'danger' })
let pendingDelete = null

function showModal(title, message, type = 'confirm', variant = 'danger') {
  modal.value = { show: true, title, message, type, variant }
}

// ==================== DASHBOARD ====================
const stats = ref(null)

async function fetchStats() {
  try {
    const { data } = await api.get('/api/admin/stats')
    stats.value = data
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

// ==================== USERS ====================
const users = ref([])
const usersPage = ref(1)
const usersTotal = ref(0)
const usersPages = ref(0)
const userKeyword = ref('')
const editingUserId = ref(null)
const editForm = ref({ role: '', credit: 0 })

async function fetchUsers() {
  try {
    const params = { page: usersPage.value }
    if (userKeyword.value) params.keyword = userKeyword.value
    const { data } = await api.get('/api/admin/users', { params })
    users.value = data.items
    usersTotal.value = data.total
    usersPages.value = data.pages
  } catch (e) {
    console.error('Failed to fetch users:', e)
  }
}

function startEdit(u) {
  editingUserId.value = u.id
  editForm.value = { role: u.role, credit: u.credit }
}

function cancelEdit() {
  editingUserId.value = null
}

async function saveEdit(u) {
  try {
    await api.put(`/api/admin/users/${u.id}`, editForm.value)
    u.role = editForm.value.role
    u.credit = editForm.value.credit
    editingUserId.value = null
  } catch (e) {
    console.error('Failed to update user:', e)
  }
}

// ==================== PRODUCTS ====================
const products = ref([])
const productsPage = ref(1)
const productsTotal = ref(0)
const productsPages = ref(0)
const prodKeyword = ref('')
const prodStatusFilter = ref('')

const statusLabels = { onsale: '在售', reserved: '预留', sold: '已售', removed: '已下架' }
const statusColors = { onsale: 'bg-green-100 text-green-700', reserved: 'bg-yellow-100 text-yellow-700', sold: 'bg-slate-100 text-slate-500', removed: 'bg-red-100 text-red-500' }

async function fetchProducts() {
  try {
    const params = { page: productsPage.value }
    if (prodKeyword.value) params.keyword = prodKeyword.value
    if (prodStatusFilter.value) params.status = prodStatusFilter.value
    const { data } = await api.get('/api/admin/products', { params })
    products.value = data.items
    productsTotal.value = data.total
    productsPages.value = data.pages
  } catch (e) {
    console.error('Failed to fetch products:', e)
  }
}

function confirmDelete(pid) {
  pendingDelete = pid
  showModal('确认删除', '确定要强制删除该商品吗？此操作不可撤销。', 'confirm', 'danger')
}

async function doDelete() {
  if (!pendingDelete) return
  try {
    await api.delete(`/api/admin/products/${pendingDelete}`)
    pendingDelete = null
    fetchProducts()
    showModal('删除成功', '商品已强制删除', 'alert', 'primary')
  } catch (e) {
    console.error('Failed to delete product:', e)
    showModal('删除失败', '删除商品时出错', 'alert', 'danger')
  }
}

function handleModalConfirm() {
  if (modal.value.type === 'confirm' && modal.value.variant === 'danger') {
    doDelete()
  }
  modal.value.show = false
}

function viewProduct(id) {
  router.push(`/product/${id}`)
}

// ==================== WATCH ====================
watch(activeTab, (tab) => {
  if (tab === 'dashboard') fetchStats()
  else if (tab === 'users') fetchUsers()
  else if (tab === 'products') fetchProducts()
})

watch(usersPage, fetchUsers)
watch(productsPage, fetchProducts)
watch(prodStatusFilter, () => { productsPage.value = 1; fetchProducts() })

// Debounced search
let userSearchTimer = null
watch(userKeyword, () => {
  clearTimeout(userSearchTimer)
  userSearchTimer = setTimeout(() => { usersPage.value = 1; fetchUsers() }, 300)
})

let prodSearchTimer = null
watch(prodKeyword, () => {
  clearTimeout(prodSearchTimer)
  prodSearchTimer = setTimeout(() => { productsPage.value = 1; fetchProducts() }, 300)
})

onMounted(fetchStats)
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-display font-bold text-slate-800">管理后台</h1>

    <!-- Tabs -->
    <div class="flex gap-1 bg-white rounded-xl p-1 shadow-sm border border-warm-100">
      <button @click="activeTab = 'dashboard'" data-testid="admin-tab-overview"
        :class="['px-5 py-2 rounded-lg text-sm font-medium transition-all', activeTab === 'dashboard' ? 'bg-coral-500 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 hover:bg-warm-50']">
        概览
      </button>
      <button @click="activeTab = 'users'" data-testid="admin-tab-users"
        :class="['px-5 py-2 rounded-lg text-sm font-medium transition-all', activeTab === 'users' ? 'bg-coral-500 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 hover:bg-warm-50']">
        用户管理
      </button>
      <button @click="activeTab = 'products'" data-testid="admin-tab-products"
        :class="['px-5 py-2 rounded-lg text-sm font-medium transition-all', activeTab === 'products' ? 'bg-coral-500 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 hover:bg-warm-50']">
        商品管理
      </button>
    </div>

    <!-- ==================== DASHBOARD TAB ==================== -->
    <div v-if="activeTab === 'dashboard' && stats">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">用户总数</span>
          </div>
          <p class="text-3xl font-bold text-slate-800">{{ stats.total_users }}</p>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">商品总数</span>
          </div>
          <p class="text-3xl font-bold text-slate-800">{{ stats.total_products }}</p>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 21L3 16.5m0 0L7.5 11M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">交易总数</span>
          </div>
          <p class="text-3xl font-bold text-slate-800">{{ stats.total_transactions }}</p>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-purple-50 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">评价总数</span>
          </div>
          <p class="text-3xl font-bold text-slate-800">{{ stats.total_reviews }}</p>
        </div>
      </div>

      <!-- Product status breakdown -->
      <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5 mb-6">
        <h3 class="text-sm font-semibold text-slate-600 mb-3">商品状态分布</h3>
        <div class="flex gap-4">
          <div v-for="(count, status) in stats.products_by_status" :key="status"
            class="flex items-center gap-2 text-sm">
            <span :class="['w-2.5 h-2.5 rounded-full', { 'bg-green-400': status === 'onsale', 'bg-yellow-400': status === 'reserved', 'bg-slate-400': status === 'sold', 'bg-red-400': status === 'removed' }]"></span>
            <span class="text-slate-500">{{ statusLabels[status] || status }}</span>
            <span class="font-semibold text-slate-800">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Recent users + transactions -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
          <h3 class="text-sm font-semibold text-slate-600 mb-3">最近注册用户</h3>
          <table class="w-full text-sm">
            <thead><tr class="text-left text-slate-400 text-xs"><th class="pb-2 font-medium">学号</th><th class="pb-2 font-medium">昵称</th><th class="pb-2 font-medium">时间</th></tr></thead>
            <tbody>
              <tr v-for="u in stats.recent_users" :key="u.id" class="border-t border-warm-50">
                <td class="py-2 text-slate-600">{{ u.student_id }}</td>
                <td class="py-2">
                  <span class="text-slate-800">{{ u.nickname }}</span>
                  <span v-if="u.role === 'admin'" class="ml-1.5 text-xs bg-coral-100 text-coral-600 px-1.5 py-0.5 rounded">admin</span>
                </td>
                <td class="py-2 text-slate-400 text-xs">{{ u.created_at?.slice(0, 10) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
          <h3 class="text-sm font-semibold text-slate-600 mb-3">最近交易</h3>
          <table class="w-full text-sm">
            <thead><tr class="text-left text-slate-400 text-xs"><th class="pb-2 font-medium">商品</th><th class="pb-2 font-medium">买家</th><th class="pb-2 font-medium">状态</th></tr></thead>
            <tbody>
              <tr v-for="t in stats.recent_transactions" :key="t.id" class="border-t border-warm-50">
                <td class="py-2 text-slate-600 truncate max-w-[120px]">{{ t.product_title }}</td>
                <td class="py-2 text-slate-600">{{ t.buyer_nickname }}</td>
                <td class="py-2"><span class="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{{ t.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== USERS TAB ==================== -->
    <div v-if="activeTab === 'users'">
      <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
        <!-- Search -->
        <div class="mb-4">
          <input v-model="userKeyword" placeholder="搜索学号/昵称/邮箱..." class="input-fancy w-full max-w-xs" />
        </div>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-slate-400 text-xs border-b border-warm-100">
              <th class="pb-3 font-medium">ID</th>
              <th class="pb-3 font-medium">学号</th>
              <th class="pb-3 font-medium">昵称</th>
              <th class="pb-3 font-medium">邮箱</th>
              <th class="pb-3 font-medium">信用分</th>
              <th class="pb-3 font-medium">角色</th>
              <th class="pb-3 font-medium">注册时间</th>
              <th class="pb-3 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="border-b border-warm-50 hover:bg-warm-50/50 transition">
              <td class="py-3 text-slate-400 text-xs">{{ u.id }}</td>
              <td class="py-3 text-slate-600 font-mono text-xs">{{ u.student_id }}</td>
              <td class="py-3 text-slate-800 font-medium">{{ u.nickname }}</td>
              <td class="py-3 text-slate-500 text-xs">{{ u.email }}</td>
              <td class="py-3">
                <template v-if="editingUserId === u.id">
                  <input v-model.number="editForm.credit" type="number" min="0" max="200" class="w-16 input-fancy text-xs py-1 px-2" />
                </template>
                <template v-else>
                  <span :class="['font-medium', u.credit >= 100 ? 'text-green-600' : 'text-red-500']">{{ u.credit }}</span>
                </template>
              </td>
              <td class="py-3">
                <template v-if="editingUserId === u.id">
                  <select v-model="editForm.role" class="input-fancy text-xs py-1 px-2">
                    <option value="user">user</option>
                    <option value="admin">admin</option>
                  </select>
                </template>
                <template v-else>
                  <span :class="['text-xs px-2 py-0.5 rounded', u.role === 'admin' ? 'bg-coral-100 text-coral-600' : 'bg-slate-100 text-slate-500']">{{ u.role }}</span>
                </template>
              </td>
              <td class="py-3 text-slate-400 text-xs">{{ u.created_at?.slice(0, 10) }}</td>
              <td class="py-3">
                <template v-if="editingUserId === u.id">
                  <button @click="saveEdit(u)" class="text-xs text-green-600 hover:text-green-700 font-medium mr-2">保存</button>
                  <button @click="cancelEdit()" class="text-xs text-slate-400 hover:text-slate-600">取消</button>
                </template>
                <button v-else @click="startEdit(u)" class="text-xs text-coral-500 hover:text-coral-600 font-medium">编辑</button>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- Pagination -->
        <div v-if="usersPages > 1" class="flex items-center justify-between mt-4 pt-4 border-t border-warm-100">
          <span class="text-xs text-slate-400">共 {{ usersTotal }} 条</span>
          <div class="flex gap-1">
            <button @click="usersPage = Math.max(1, usersPage - 1)" :disabled="usersPage <= 1"
              class="px-3 py-1 text-xs rounded-lg border border-warm-200 text-slate-500 hover:bg-warm-50 disabled:opacity-30 transition">上一页</button>
            <span class="px-3 py-1 text-xs text-slate-500">{{ usersPage }} / {{ usersPages }}</span>
            <button @click="usersPage = Math.min(usersPages, usersPage + 1)" :disabled="usersPage >= usersPages"
              class="px-3 py-1 text-xs rounded-lg border border-warm-200 text-slate-500 hover:bg-warm-50 disabled:opacity-30 transition">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== PRODUCTS TAB ==================== -->
    <div v-if="activeTab === 'products'">
      <div class="bg-white rounded-2xl shadow-sm border border-warm-100 p-5">
        <!-- Filters -->
        <div class="flex flex-wrap gap-3 mb-4 items-center">
          <input v-model="prodKeyword" placeholder="搜索商品标题/描述..." class="input-fancy w-full max-w-xs" />
          <div class="flex gap-1">
            <button @click="prodStatusFilter = ''"
              :class="['px-3 py-1.5 text-xs rounded-lg font-medium transition', !prodStatusFilter ? 'bg-coral-500 text-white' : 'bg-warm-50 text-slate-500 hover:bg-warm-100']">全部</button>
            <button v-for="s in ['onsale', 'reserved', 'sold', 'removed']" :key="s" @click="prodStatusFilter = s"
              :class="['px-3 py-1.5 text-xs rounded-lg font-medium transition', prodStatusFilter === s ? 'bg-coral-500 text-white' : 'bg-warm-50 text-slate-500 hover:bg-warm-100']">{{ statusLabels[s] }}</button>
          </div>
        </div>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-slate-400 text-xs border-b border-warm-100">
              <th class="pb-3 font-medium">ID</th>
              <th class="pb-3 font-medium">标题</th>
              <th class="pb-3 font-medium">分类</th>
              <th class="pb-3 font-medium">价格</th>
              <th class="pb-3 font-medium">状态</th>
              <th class="pb-3 font-medium">卖家</th>
              <th class="pb-3 font-medium">发布时间</th>
              <th class="pb-3 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in products" :key="p.id" class="border-b border-warm-50 hover:bg-warm-50/50 transition">
              <td class="py-3 text-slate-400 text-xs">{{ p.id }}</td>
              <td class="py-3 text-slate-800 font-medium max-w-[180px] truncate">{{ p.title }}</td>
              <td class="py-3 text-slate-500 text-xs">{{ p.category }}</td>
              <td class="py-3 text-slate-700 font-medium">¥{{ p.price }}</td>
              <td class="py-3"><span :class="['text-xs px-2 py-0.5 rounded', statusColors[p.status]]">{{ statusLabels[p.status] }}</span></td>
              <td class="py-3 text-slate-500 text-xs">{{ p.seller_nickname }}</td>
              <td class="py-3 text-slate-400 text-xs">{{ p.created_at?.slice(0, 10) }}</td>
              <td class="py-3">
                <button @click="viewProduct(p.id)" class="text-xs text-blue-500 hover:text-blue-600 font-medium mr-3">查看</button>
                <button @click="confirmDelete(p.id)" class="text-xs text-red-400 hover:text-red-600 font-medium">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- Pagination -->
        <div v-if="productsPages > 1" class="flex items-center justify-between mt-4 pt-4 border-t border-warm-100">
          <span class="text-xs text-slate-400">共 {{ productsTotal }} 条</span>
          <div class="flex gap-1">
            <button @click="productsPage = Math.max(1, productsPage - 1)" :disabled="productsPage <= 1"
              class="px-3 py-1 text-xs rounded-lg border border-warm-200 text-slate-500 hover:bg-warm-50 disabled:opacity-30 transition">上一页</button>
            <span class="px-3 py-1 text-xs text-slate-500">{{ productsPage }} / {{ productsPages }}</span>
            <button @click="productsPage = Math.min(productsPages, productsPage + 1)" :disabled="productsPage >= productsPages"
              class="px-3 py-1 text-xs rounded-lg border border-warm-200 text-slate-500 hover:bg-warm-50 disabled:opacity-30 transition">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Modal
      :show="modal.show"
      :title="modal.title"
      :message="modal.message"
      :type="modal.type"
      :variant="modal.variant"
      confirmText="确认删除"
      @confirm="handleModalConfirm"
      @cancel="modal.show = false"
      @update:show="modal.show = $event"
    />
  </div>
</template>
