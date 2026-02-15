<template>
  <div class="analytics">
    <h1>Analytics</h1>

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
          label="Total Customers"
          :value="stats.today?.new_customers || 0"
          icon="User"
          color="primary"
        />
      </el-col>

      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="Messages Sent"
          :value="stats.today?.emails_sent || 0"
          icon="Promotion"
          color="success"
        />
      </el-col>

      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="Replies"
          :value="stats.today?.emails_replied || 0"
          icon="ChatDotRound"
          color="warning"
        />
      </el-col>

      <el-col
        :xs="24"
        :sm="12"
        :md="6"
      >
        <StatCard
          label="Conversions"
          :value="stats.today?.converted_customers || 0"
          icon="TrendCharts"
          color="danger"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col
        :xs="24"
        :lg="16"
      >
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Trends</span>
              <el-radio-group
                v-model="trendPeriod"
                size="small"
              >
                <el-radio-button label="week">
                  Week
                </el-radio-button>
                <el-radio-button label="month">
                  Month
                </el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div
            class="chart-container"
            style="height: 350px"
          >
            <el-empty description="Trends chart coming soon" />
          </div>
        </el-card>
      </el-col>

      <el-col
        :xs="24"
        :lg="8"
      >
        <el-card>
          <template #header>
            Conversion Funnel
          </template>
          <div class="funnel-preview">
            <div
              v-for="(stage, i) in funnelStages"
              :key="stage.name"
              class="funnel-item"
              :style="{ width: getFunnelWidth(i) }"
            >
              <span>{{ stage.name }}</span>
              <span class="funnel-value">{{ stage.value }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'
import type { DashboardStats } from '@/types'
import StatCard from '@/components/Dashboard/StatCard.vue'

const stats = ref<DashboardStats | null>(null)

const trendPeriod = ref('week')

const funnelStages = [
  { name: 'Total', value: 1000 },
  { name: 'Contacted', value: 700 },
  { name: 'Engaged', value: 300 },
  { name: 'Replied', value: 120 },
  { name: 'Converted', value: 25 },
]

async function fetchStats() {
  try {
    const response = await api.get<DashboardStats>('/api/v1/stats/dashboard')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

function getFunnelWidth(index: number) {
  const widths = ['100%', '90%', '80%', '70%', '60%', '50%']
  return widths[index] || '100%'
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="scss" scoped>
.analytics {
  h1 {
    margin-bottom: 20px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.chart-container {
  .el-empty {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.funnel-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

.funnel-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  font-size: 14px;
}

.funnel-value {
  font-weight: 600;
  color: var(--el-color-primary);
}
</style>
