<template>
  <div class="conversation-list">
    <div class="list-header">
      <el-input
        v-model="searchQuery"
        placeholder="Search conversations..."
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-dropdown trigger="click">
        <el-button>
          {{ statusFilter }}
          <el-icon class="el-icon--right">
            <ArrowDown />
          </el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="statusFilter = 'All'">
              All
            </el-dropdown-item>
            <el-dropdown-item @click="statusFilter = 'Active'">
              Active
            </el-dropdown-item>
            <el-dropdown-item @click="statusFilter = 'High Intent'">
              High Intent
            </el-dropdown-item>
            <el-dropdown-item @click="statusFilter = 'Awaiting'">
              Awaiting Reply
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div class="list-content">
      <div
        v-for="conversation in filteredConversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ 'active': activeConversationId === conversation.id, 'unread': conversation.unread }"
        @click="selectConversation(conversation.id)"
      >
        <div class="conversation-avatar">
          <el-avatar
            v-if="conversation.customerAvatar"
            :size="40"
            :src="conversation.customerAvatar"
          />
          <el-avatar
            v-else
            :size="40"
          >
            {{ conversation.customerName?.charAt(0).toUpperCase() }}
          </el-avatar>
          <el-badge
            v-if="conversation.unreadCount > 0"
            :value="conversation.unreadCount"
            class="unread-badge"
          />
        </div>

        <div class="conversation-info">
          <div class="conversation-name">
            {{ conversation.customerName }}
          </div>
          <div class="conversation-preview">
            {{ conversation.lastMessage }}
          </div>
          <div class="conversation-meta">
            <el-tag
              v-if="conversation.status === 'active'"
              type="success"
              size="small"
            >
              Active
            </el-tag>
            <el-tag
              v-if="conversation.intentLevel === 'high'"
              type="warning"
              size="small"
            >
              High Intent
            </el-tag>
            <el-tag
              v-if="conversation.manualTakeover"
              type="danger"
              size="small"
            >
              Manual
            </el-tag>
            <span class="conversation-time">{{ formatTime(conversation.lastMessageAt) }}</span>
          </div>
        </div>
      </div>

      <el-empty
        v-if="filteredConversations.length === 0"
        description="No conversations found"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

interface Props {
  conversations?: any[]
  activeConversationId?: string
}

const props = withDefaults(defineProps<Props>(), {
  conversations: () => [],
  activeConversationId: '',
})

const emit = defineEmits<{
  'select': [id: string]
}>()

const searchQuery = ref('')
const statusFilter = ref('All')

const filteredConversations = computed(() => {
  let result = props.conversations

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((c) =>
      c.customerName?.toLowerCase().includes(query) ||
      c.lastMessage?.toLowerCase().includes(query)
    )
  }

  // Filter by status
  if (statusFilter.value === 'Active') {
    result = result.filter((c) => c.status === 'active')
  } else if (statusFilter.value === 'High Intent') {
    result = result.filter((c) => c.intentLevel === 'high' || c.intentLevel === 'very_high')
  } else if (statusFilter.value === 'Awaiting') {
    result = result.filter((c) => c.awaitingReply)
  }

  return result
})

function selectConversation(id: string) {
  emit('select', id)
}

function formatTime(date?: string) {
  if (!date) return ''

  const diff = dayjs().diff(dayjs(date), 'day')

  if (diff > 0) {
    return dayjs(date).format('MMM DD')
  } else {
    return dayjs(date).fromNow()
  }
}
</script>

<style lang="scss" scoped>
.conversation-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: 1px solid var(--el-border-color);
  background: var(--el-bg-color-page);
}

.list-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  gap: 8px;
}

.list-content {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--el-border-color-light);
  transition: background-color 0.2s;

  &:hover {
    background: var(--el-fill-color-light);
  }

  &.active {
    background: var(--el-color-primary-light-9);
    border-left: 3px solid var(--el-color-primary);
  }

  &.unread {
    .conversation-name {
      font-weight: 600;
    }
  }
}

.conversation-avatar {
  position: relative;
  flex-shrink: 0;
}

.unread-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
}

.conversation-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.conversation-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-preview {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.conversation-time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
</style>
