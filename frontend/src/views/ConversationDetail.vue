<template>
  <div class="conversation-detail">
    <el-page-header @back="$router.back()">
      <template #content>
        <span class="text-large font-600 mr-3">Conversation: {{ conversationId }}</span>
      </template>
    </el-page-header>

    <div class="conversation-content">
      <el-card class="messages-panel">
        <div class="messages-list">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="['message-item', message.role]"
          >
            <div class="message-bubble">
              <div class="message-role">
                {{ message.role }}
              </div>
              <div class="message-content">
                {{ message.content }}
              </div>
              <div class="message-time">
                {{ formatTime(message.sent_at) }}
              </div>
            </div>
          </div>
        </div>

        <div class="message-input">
          <el-input
            v-model="newMessage"
            type="textarea"
            placeholder="Type your message..."
            @keyup.ctrl.enter="sendMessage"
          />
          <el-button
            type="primary"
            :loading="sending"
            @click="sendMessage"
          >
            Send (Ctrl+Enter)
          </el-button>
        </div>
      </el-card>

      <el-card class="info-panel">
        <template #header>
          Conversation Info
        </template>
        <el-descriptions
          :column="1"
          border
        >
          <el-descriptions-item label="Platform">
            {{ conversation?.platform }}
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag>{{ conversation?.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Intent">
            {{ conversation?.current_intent }}
          </el-descriptions-item>
          <el-descriptions-item label="AI Handled">
            <el-tag :type="conversation?.ai_handled ? 'success' : 'info'">
              {{ conversation?.ai_handled ? 'Yes' : 'No' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <el-button
          v-if="conversation?.ai_handled"
          type="warning"
          @click="takeover"
        >
          Take Over
        </el-button>
        <el-button
          v-if="conversation?.manual_takeover"
          @click="release"
        >
          Release to AI
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'

const route = useRoute()

const conversationId = route.params.id as string
const conversation = ref<any>(null)
const messages = ref<any[]>([])
const newMessage = ref('')
const sending = ref(false)

async function fetchConversation() {
  try {
    const response = await api.get(`/api/v1/conversations/${conversationId}`)
    conversation.value = response.data
    messages.value = response.data.messages
  } catch {
    ElMessage.error('Failed to load conversation')
  }
}

async function sendMessage() {
  if (!newMessage.value.trim()) return

  sending.value = true
  try {
    await api.post(`/api/v1/conversations/${conversationId}/messages`, {
      role: 'user',
      content: newMessage.value,
    })
    newMessage.value = ''
    await fetchConversation()
  } catch {
    ElMessage.error('Failed to send message')
  } finally {
    sending.value = false
  }
}

async function takeover() {
  try {
    await api.post(`/api/v1/conversations/${conversationId}/takeover`)
    ElMessage.success('Conversation taken over')
    await fetchConversation()
  } catch {
    ElMessage.error('Failed to take over')
  }
}

async function release() {
  try {
    await api.post(`/api/v1/conversations/${conversationId}/release`)
    ElMessage.success('Conversation released')
    await fetchConversation()
  } catch {
    ElMessage.error('Failed to release')
  }
}

function formatTime(date: string) {
  return new Date(date).toLocaleTimeString()
}

onMounted(() => {
  fetchConversation()
})
</script>

<style lang="scss" scoped>
.conversation-detail {
  .text-large {
    font-size: 20px;
  }

  .conversation-content {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 20px;
    margin-top: 20px;
  }

  .messages-panel {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 200px);
  }

  .messages-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .message-item {
    margin-bottom: 16px;

    &.user {
      .message-bubble {
        background: var(--el-color-primary);
        color: white;
        margin-left: auto;
      }
    }

    &.assistant {
      .message-bubble {
        background: var(--el-fill-color-light);
      }
    }
  }

  .message-bubble {
    max-width: 70%;
    padding: 12px;
    border-radius: 12px;

    .message-role {
      font-size: 12px;
      opacity: 0.8;
      margin-bottom: 4px;
    }

    .message-content {
      line-height: 1.5;
    }

    .message-time {
      font-size: 12px;
      opacity: 0.6;
      margin-top: 8px;
      text-align: right;
    }
  }

  .message-input {
    padding: 16px;
    border-top: 1px solid var(--el-border-color);

    .el-textarea {
      margin-bottom: 12px;
    }
  }

  .info-panel {
    height: fit-content;
  }
}
</style>
