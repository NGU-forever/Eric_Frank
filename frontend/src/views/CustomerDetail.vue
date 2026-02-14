<template>
  <div class="customer-detail">
    <el-page-header @back="$router.back()">
      <template #content>
        <span class="text-large font-600 mr-3">{{ customer?.username }}</span>
      </template>
    </el-page-header>

    <el-descriptions
      v-if="customer"
      :column="3"
      border
      style="margin-top: 20px"
    >
      <el-descriptions-item label="Email">
        {{ customer.email }}
      </el-descriptions-item>
      <el-descriptions-item label="WhatsApp">
        {{ customer.whatsapp }}
      </el-descriptions-item>
      <el-descriptions-item label="Platform">
        {{ customer.platform }}
      </el-descriptions-item>
      <el-descriptions-item label="Country">
        {{ customer.country }}
      </el-descriptions-item>
      <el-descriptions-item label="Category">
        {{ customer.category }}
      </el-descriptions-item>
      <el-descriptions-item label="Followers">
        {{ customer.follower_count }}
      </el-descriptions-item>
      <el-descriptions-item label="Status">
        <el-tag :type="getStatusType(customer.status)">
          {{ customer.status }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="Intent Level">
        <el-tag
          v-if="customer.intent_level"
          :type="getIntentType(customer.intent_level)"
        >
          {{ customer.intent_level }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="Tags">
        <el-tag
          v-for="tag in customer.tags"
          :key="tag"
          style="margin-right: 4px"
        >
          {{ tag }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { customerApi } from '@/api/customer'

const route = useRoute()
const customer = ref<any>(null)

async function fetchCustomer() {
  try {
    customer.value = await customerApi.get(Number(route.params.id))
  } catch {
    // Handle error
  }
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    new: 'info',
    contacted: 'primary',
    engaged: 'warning',
    converted: 'success',
    lost: 'danger',
  }
  return types[status] || 'info'
}

function getIntentType(level: string) {
  const types: Record<string, any> = {
    low: 'info',
    medium: 'primary',
    high: 'warning',
    very_high: 'success',
  }
  return types[level] || 'info'
}

onMounted(() => {
  fetchCustomer()
})
</script>

<style lang="scss" scoped>
.customer-detail {
  .text-large {
    font-size: 20px;
  }
}
</style>
