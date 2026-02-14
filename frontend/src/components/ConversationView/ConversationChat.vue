<template>
  <div class="conversation-chat">
    <div class="chat-header">
      <div class="chat-customer">
        <el-avatar
          :size="40"
          :src="customer?.avatar"
        >
          {{ customer?.name?.charAt(0) }}
        </el-avatar>
        <div class="customer-info">
          <div class="customer-name">
            {{ customer?.name }}
          </div>
          <div class="customer-meta">
            <el-tag
              size="small"
              :type="getStatusType(customer?.status)"
            >
              {{ customer?.status }}
            </el-tag>
            <span
              v-if="customer?.intent"
              class="customer-intent"
            >{{ customer.intent }}</span>
          </div>
        </div>
      </div>

      <div class="chat-actions">
        <el-button
          v-if="!isTakenOver"
          type="warning"
          size="small"
          @click="takeover"
        >
          <el-icon><User /></el-icon>
          Take Over
        </el-button>
        <el-button
          v-else
          type="success"
          size="small"
          @click="release"
        >
          <el-icon><ChatDotRound /></el-icon>
          Release
        </el-button>
      </div>
    </div>

    <div
      ref="messagesRef"
      class="chat-messages"
    >
      <div
        v-for="(group, date) in groupedMessages"
        :key="date"
        class="message-group"
      >
        <div class="message-date">
          {{ formatDate(date) }}
        </div>
        <div
          v-for="message in group"
          :key="message.id"
          :class="['message', message.role]"
        >
          <div class="message-bubble">
            <div
              v-if="message.role === 'assistant'"
              class="ai-badge"
            >
              <el-icon><MagicStick /></el-icon>
              AI Generated
            </div>
            <div class="message-content">
              {{ message.content }}
            </div>
            <div class="message-time">
              {{ formatTime(message.sentAt) }}
            </div>
          </div>

          <!-- Suggested actions -->
          <div
            v-if="message.role === 'assistant' && message.suggestedActions?.length"
            class="suggested-actions"
          >
            <el-button
              v-for="action in message.suggestedActions"
              :key="action"
              size="small"
              type="primary"
              plain
              @click="executeAction(action)"
            >
              {{ formatAction(action) }}
            </el-button>
          </div>
        </div>
      </div>

      <el-empty
        v-if="messages.length === 0"
        description="No messages yet"
      />
    </div>

    <div class="chat-input">
      <div
        v-if="customer?.intent"
        class="intent-indicator"
      >
        <el-icon><TrendCharts /></el-icon>
        <span>Detected Intent: {{ customer.intent }}</span>
        <el-tag
          size="small"
          :type="getIntentType(customer.intentLevel)"
        >
          {{ customer.intentLevel }}
        </el-tag>
      </div>

      <el-input
        v-model="newMessage"
        type="textarea"
        :rows="3"
        placeholder="Type your message... (Ctrl+Enter to send)"
        :disabled="isSending"
        @keydown.ctrl.enter="sendMessage"
      />

      <div class="input-actions">
        <el-space>
          <el-button
            icon="Paperclip"
            circle
            @click="attachFile"
          />
          <el-button
            type="primary"
            icon="Promotion"
            :loading="isSending"
            @click="sendMessage"
          >
            Send
          </el-button>
        </el-space>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

interface Props {
  messages?: any[]
  customer?: any
  isTakenOver?: boolean
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  messages: () => [],
  customer: null,
  isTakenOver: false,
  isLoading: false,
})

const emit = defineEmits<{
  'send-message': [message: string]
  'takeover': []
  'release': []
  'execute-action': [action: string]
}>()

const messagesRef = ref<HTMLElement>()
const newMessage = ref('')
const isSending = ref(false)

// Group messages by date
const groupedMessages = computed(() => {
  const groups: Record<string, any[]> = {}

  props.messages.forEach((message) => {
    const date = dayjs(message.sentAt).format('YYYY-MM-DD')
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(message)
  })

  return groups
})

function sendMessage() {
  if (!newMessage.value.trim() || isSending.value) return

  isSending.value = true

  emit('send-message', newMessage.value)
  newMessage.value = ''

  setTimeout(() => {
    isSending.value = false
    scrollToBottom()
  }, 500)
}

function takeover() {
  emit('takeover')
  ElMessage.info('Conversation taken over')
}

function release() {
  emit('release')
  ElMessage.info('Conversation released to AI')
}

function attachFile() {
  ElMessage.info('File attachment feature coming soon')
}

function executeAction(action: string) {
  emit('execute-action', action)
  ElMessage.success(`Executing action: ${action}`)
}

function formatAction(action: string) {
  // Convert snake_case to readable format
  return action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    active: 'success',
    paused: 'warning',
    closed: 'info',
  }
  return types[status] || 'info'
}

function getIntentType(level: string) {
  const types: Record<string, any> = {
    low: 'info',
    medium: 'primary',
    high: 'warning',
    very_high: 'danger',
  }
  return types[level] || 'info'
}

function formatDate(date: string) {
  const today = dayjs().format('YYYY-MM-DD')
  const msgDate = dayjs(date).format('YYYY-MM-DD')

  if (today === msgDate) {
    return 'Today'
  }

  return dayjs(date).format('MMM DD, YYYY')
}

function formatTime(date: string) {
  return dayjs(date).format('HH:mm')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  scrollToBottom()
})

// Watch for new messages and scroll
// import { watch } from 'vue'
// watch(() => props.messages.length, scrollToBottom)
</script>

<style lang="scss" scoped>
.conversation-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--el-bg-color-page);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
}

.chat-customer {
  display: flex;
  align-items: center;
  gap: 12px;
}

.customer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.customer-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.customer-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-intent {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--el-fill-color-blank);
}

.message-group {
  margin-bottom: 24px;
}

.message-date {
  text-align: center;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  margin-bottom: 12px;
}

.message {
  display: flex;
  margin-bottom: 16px;

  &.user {
    justify-content: flex-end;

    .message-bubble {
      background: var(--el-color-primary);
      color: white;
      border-radius: 16px 16px 4px 16px;
    }
  }

  &.assistant {
    justify-content: flex-start;

    .message-bubble {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 16px 16px 16px 4px;
    }
  }
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  position: relative;
}

.ai-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--el-color-success);
  margin-bottom: 6px;
}

.message-content {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

.suggested-actions {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
}

.intent-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
