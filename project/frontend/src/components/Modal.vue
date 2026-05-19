<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  show: Boolean,
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' },
  type: { type: String, default: 'confirm' }, // confirm / alert / prompt
  variant: { type: String, default: 'primary' }, // primary / danger
})

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

function onConfirm() {
  emit('confirm')
  emit('update:show', false)
}
function onCancel() {
  emit('cancel')
  emit('update:show', false)
}

function onKeydown(e) {
  if (e.key === 'Escape') onCancel()
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="onCancel">
        <!-- 遮罩 -->
        <div class="absolute inset-0 bg-black/30 backdrop-blur-[2px]"></div>
        <!-- 弹窗 -->
        <div class="relative bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 border border-warm-100"
          @click.stop>
          <div v-if="title" class="font-display text-lg font-bold text-slate-800 mb-2">{{ title }}</div>
          <p class="text-sm text-slate-600 leading-relaxed">{{ message }}</p>

          <div class="flex gap-2.5 mt-5 justify-end">
            <button v-if="type === 'confirm'" @click="onCancel"
              class="px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 text-slate-600 hover:bg-slate-50 transition btn-press">
              {{ cancelText }}
            </button>
            <button @click="onConfirm"
              :class="variant === 'danger' ? 'bg-coral-500 hover:bg-coral-600 shadow-coral-200' : 'bg-coral-500 hover:bg-coral-600 shadow-coral-200'"
              class="px-4 py-2 rounded-xl text-sm font-medium text-white transition btn-press shadow-sm">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active { transition: all 0.2s ease-out; }
.modal-leave-active { transition: all 0.15s ease-in; }
.modal-enter-from { opacity: 0; }
.modal-enter-from > div:last-child { transform: scale(0.95); }
.modal-leave-to { opacity: 0; }
</style>
