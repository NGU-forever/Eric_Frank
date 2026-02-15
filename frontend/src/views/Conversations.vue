<template>
  <div class="conversations">
    <h1>Conversations</h1>

    <el-card>
      <el-table
        v-loading="loading"
        :data="conversations"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="200"
        />
        <el-table-column
          prop="customer_id"
          label="Customer ID"
          width="100"
        />
        <el-table-column
          prop="platform"
          label="Platform"
        />
        <el-table-column
          prop="status"
          label="Status"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="current_intent"
          label="Intent"
        />
        <el-table-column
          prop="last_message_at"
          label="Last Message"
        >
          <template #default="{ row }">
            {{ formatDate(row.last_message_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="Actions"
          width="150"
        >
          <template #default="{ row }">
            <el-button
              text
              @click="viewConversation(row.id)"
            >
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'

const router = useRouter()

const loading = ref(false)
const conversations = ref<any[]>([])

async function fetchConversations() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/conversations')
    conversations.value = response.data
  } finally {
    loading.value = false
  }
}

function viewConversation(id: string) {
  router.push(`/conversations/${id}`)
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    active: 'success',
    paused: 'warning',
    closed: 'info',
    archived: 'info',
  }
  return types[status] || 'info'
}

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

onMounted(() => {
  fetchConversations()
})
</script>

<style lang="scss" scoped>
.conversations {
  h1 {
    margin-bottom: 20px;
  }
}
</style>
