<template>
  <el-card
    class="stat-card"
    shadow="hover"
  >
    <div class="stat-content">
      <div class="stat-icon">
        <component
          :is="icon"
          :size="32"
        />
      </div>
      <div class="stat-info">
        <div class="stat-value">
          {{ value.toLocaleString() }}
        </div>
        <div class="stat-label">
          {{ label }}
        </div>
        <div
          v-if="trend !== undefined"
          class="stat-trend"
        >
          <el-icon>
            <component :is="trend > 0 ? 'TrendCharts' : 'Bottom'" />
          </el-icon>
          <span :class="trend > 0 ? 'trend-up' : 'trend-down'">
            {{ Math.abs(trend) }}%
          </span>
          <span class="trend-period">vs last {{ period }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'

interface Props {
  label: string
  value: number
  suffix?: string
  trend?: number
  period?: string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  icon?: any
}

const props = withDefaults(defineProps<Props>(), {
  suffix: '',
  period: 'week',
  color: 'primary',
})

const colorClass = computed(() => `stat-icon--${props.color}`)
</script>

<style lang="scss" scoped>
.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;

  &--primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
  &--success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
  &--warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
  &--danger { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
  &--info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  margin-top: 4px;
}

.trend-up { color: var(--el-color-success); font-weight: 600; }
.trend-down { color: var(--el-color-danger); font-weight: 600; }
.trend-period { color: var(--el-text-color-placeholder); }
</style>
