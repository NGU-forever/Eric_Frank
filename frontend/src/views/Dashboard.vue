<template>
  <div class="dashboard">
    <h1>Dashboard</h1>

    <el-row
      :gutter="20"
      class="stats-row"
    >
      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="New Customers"
          :value="stats?.today?.new_customers || 0"
          :trend="stats?.trends?.customers || 0"
          period="week"
          color="primary"
          icon="User"
        />
      </el-col>

      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="Messages Sent"
          :value="stats?.today?.emails_sent || 0"
          :trend="stats?.trends?.messages || 0"
          period="week"
          color="success"
          icon="Promotion"
        />
      </el-col>

      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="Replies"
          :value="stats?.today?.emails_replied || 0"
          :trend="stats?.trends?.replies || 0"
          period="week"
          color="warning"
          icon="ChatDotRound"
        />
      </el-col>

      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="Conversions"
          :value="stats?.today?.converted_customers || 0"
          :trend="stats?.trends?.conversions || 0"
          period="week"
          color="danger"
          icon="TrendCharts"
        />
      </el-col>
    </el-row>

    <el-row
      :gutter="20"
      class="content-row"
    >
      <el-col
        :xs="24"
        :lg="16"
      >
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Recent Activity</span>
            </div>
          </template>
          <RecentActivity
            v-if="activities.length > 0"
            :activities="activities"
          />
          <el-empty
            v-else
            description="No recent activity"
          />
        </el-card>
      </el-col>

      <el-col
        :xs="24"
        :lg="8"
      >
        <el-card>
          <template #header>
            <div class="card-header">
              <span>High Intent Leads</span>
            </div>
          </template>
          <el-table
            v-loading="loading"
            :data="highIntentLeads"
            size="small"
          >
            <el-table-column
              prop="name"
              label="Name"
            />
            <el-table-column
              prop="intent"
              label="Intent"
            >
              <template #default="{ row }">
                <el-tag
                  :type="getIntentType(row.intent)"
                  size="small"
                >
                  {{ row.intent }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              label="Action"
              width="80"
            >
              <template #default="{ row }">
                <el-button
                  text
                  type="primary"
                  @click="viewLead(row)"
                >
                  View
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!loading && highIntentLeads.length === 0"
            description="No high intent leads"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { DashboardStats } from '@/types'
import StatCard from '@/components/Dashboard/StatCard.vue'
import RecentActivity from '@/components/Dashboard/RecentActivity.vue'

const router = useRouter()

const loading = ref(false)
const stats = ref<DashboardStats | null>(null)
const activities = ref<any[]>([])
const highIntentLeads = ref<any[]>([])

async function fetchStats() {
  try {
    const response = await api.get<DashboardStats>('/api/v1/stats/dashboard')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

async function fetchActivities() {
  try {
    const response = await api.get('/api/v1/stats/activities')
    activities.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch activities:', error)
  }
}

async function fetchHighIntentLeads() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/customers/high-intent')
    highIntentLeads.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch high intent leads:', error)
  } finally {
    loading.value = false
  }
}

function viewLead(lead: any) {
  router.push(`/customers/${lead.id}`)
}

function getIntentType(intent: string) {
  const types: Record<string, any> = {
    very_high: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info',
  }
  return types[intent] || 'info'
}

onMounted(() => {
  fetchStats()
  fetchActivities()
  fetchHighIntentLeads()
})
</script>

<style lang="scss" scoped>
.dashboard {
  h1 {
    margin-bottom: 24px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.content-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
</style>
