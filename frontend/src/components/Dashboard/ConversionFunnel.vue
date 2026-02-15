<template>
  <el-card class="conversion-funnel" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>Conversion Funnel</span>
        <el-dropdown trigger="click">
          <el-button text>
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="refresh">Refresh</el-dropdown-item>
              <el-dropdown-item @click="export">Export Data</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>

    <div v-loading="loading" class="funnel-content">
      <div class="funnel-chart">
        <div
          v-for="(stage, index) in stages"
          :key="stage.name"
          class="funnel-stage"
          :style="{ width: getStageWidth(index) }"
        >
          <div class="stage-bar" :style="{ background: stage.color }">
            <span class="stage-label">{{ stage.name }}</span>
            <span class="stage-value">{{ stage.value.toLocaleString() }}</span>
          </div>
          <div class="stage-rate">
            <span class="rate-label">Conversion Rate:</span>
            <span class="rate-value" :class="getRateClass(stage.rate)">
              {{ stage.rate }}%
            </span>
          </div>
        </div>
      </div>

      <div class="funnel-details">
        <div
          v-for="stage in stages"
          :key="stage.name"
          class="detail-item"
        >
          <div class="detail-color" :style="{ background: stage.color }"></div>
          <div class="detail-info">
            <div class="detail-label">{{ stage.name }}</div>
            <div class="detail-stats">
              <span class="detail-value">{{ stage.value.toLocaleString() }}</span>
              <span class="detail-rate">{{ stage.rate }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface Stage {
  name: string
  value: number
  rate: number
  color: string
}

const loading = ref(false)
const stages = ref<Stage[]>([])

const stageColors = [
  '#409eff', // blue
  '#67c23a', // green
  '#e6a23c', // orange
  '#f56c6c', // red
]

async function fetchFunnelData() {
  loading.value = true

  try {
    // Mock data - replace with API call
    const data = {
      total_customers: 1000,
      contacted: 650,
      engaged: 320,
      replied: 120,
      converted: 25,
    }

    stages.value = [
      {
        name: 'Total Customers',
        value: data.total_customers,
        rate: 100,
        color: stageColors[0],
      },
      {
        name: 'Contacted',
        value: data.contacted,
        rate: ((data.contacted / data.total_customers) * 100).toFixed(1),
        color: stageColors[1],
      },
      {
        name: 'Engaged',
        value: data.engaged,
        rate: ((data.engaged / data.contacted) * 100).toFixed(1),
        color: stageColors[2],
      },
      {
        name: 'Replied',
        value: data.replied,
        rate: ((data.replied / data.engaged) * 100).toFixed(1),
        color: stageColors[2],
      },
      {
        name: 'Converted',
        value: data.converted,
        rate: ((data.converted / data.replied) * 100).toFixed(1),
        color: stageColors[3],
      },
    ]
  } catch (error) {
    console.error('Failed to fetch funnel data:', error)
  } finally {
    loading.value = false
  }
}

function getStageWidth(index: number) {
  // Calculate width based on stage position
  const widths = ['100%', '90%', '80%', '70%', '60%']
  return widths[index] || '100%'
}

function getRateClass(rate: number) {
  if (rate >= 50) return 'rate-high'
  if (rate >= 20) return 'rate-medium'
  return 'rate-low'
}

function refresh() {
  fetchFunnelData()
  ElMessage.info('Refreshing funnel data...')
}

function exportData() {
  ElMessage.info('Exporting funnel data...')
}

onMounted(() => {
  fetchFunnelData()
})
</script>

<style lang="scss" scoped>
.conversion-funnel {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
}

.funnel-content {
  min-height: 350px;
}

.funnel-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: var(--el-fill-color-blank);
  border-radius: 8px;
  margin-bottom: 20px;
}

.funnel-stage {
  margin-bottom: 8px;
}

.stage-bar {
  width: 100%;
  padding: 12px 20px;
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stage-label {
  font-size: 14px;
}

.stage-value {
  font-size: 18px;
  font-weight: 600;
}

.stage-rate {
  text-align: center;
  margin-top: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.rate-label {
  display: block;
  margin-bottom: 2px;
  font-size: 12px;
}

.rate-value {
  font-size: 20px;
  font-weight: 700;

  &.rate-high {
    color: var(--el-color-success);
  }

  &.rate-medium {
    color: var(--el-color-warning);
  }

  &.rate-low {
    color: var(--el-color-danger);
  }
}

.funnel-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
}

.detail-color {
  width: 8px;
  height: 8px;
  border-radius: 4px;
}

.detail-info {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detail-label {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.detail-stats {
  display: flex;
  gap: 16px;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.detail-rate {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
</style>
