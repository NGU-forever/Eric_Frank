<template>
  <el-card class="alert-panel">
    <template #header>
      <div class="panel-header">
        <div class="panel-title">
          <el-icon><Bell /></el-icon>
          <span>Alerts</span>
        </div>
        <el-badge
          :value="unreadCount"
          :hidden="unreadCount === 0"
          type="danger"
        >
          <el-button @click="markAllRead">
            <el-icon><Check /></el-icon>
          </el-button>
        </el-badge>
      </div>
    </template>

    <div
      v-loading="loading"
      class="panel-content"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane
          label="All"
          name="all"
        >
          <div class="alerts-list">
            <div
              v-for="alert in allAlerts"
              :key="alert.id"
              class="alert-item"
              :class="{ 'unread': !alert.read, 'alert-' + alert.severity }"
            >
              <div class="alert-icon">
                <el-icon><component :is="getAlertIcon(alert.severity)" /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-message">
                  {{ alert.message }}
                </div>
                <div class="alert-meta">
                  <el-tag
                    size="small"
                    :type="getAlertType(alert.severity)"
                  >
                    {{ alert.severity }}
                  </el-tag>
                  <span class="alert-time">{{ formatTime(alert.createdAt) }}</span>
                </div>
              </div>
              <div class="alert-actions">
                <el-button
                  text
                  size="small"
                  @click="dismissAlert(alert.id)"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>

            <el-empty
              v-if="allAlerts.length === 0"
              description="No alerts"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="Critical"
          name="critical"
        >
          <div class="alerts-list">
            <div
              v-for="alert in criticalAlerts"
              :key="alert.id"
              class="alert-item"
              :class="{ 'unread': !alert.read, 'alert-' + alert.severity }"
            >
              <div class="alert-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-message">
                  {{ alert.message }}
                </div>
                <div class="alert-meta">
                  <el-tag
                    size="small"
                    type="danger"
                  >
                    Critical
                  </el-tag>
                  <span class="alert-time">{{ formatTime(alert.createdAt) }}</span>
                </div>
                <div class="alert-actions">
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleAlert(alert)"
                  >
                    Take Action
                  </el-button>
                </div>
              </div>
            </div>

            <el-empty
              v-if="criticalAlerts.length === 0"
              description="No critical alerts"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="Warnings"
          name="warning"
        >
          <div class="alerts-list">
            <div
              v-for="alert in warningAlerts"
              :key="alert.id"
              class="alert-item"
              :class="{ 'unread': !alert.read, 'alert-' + alert.severity }"
            >
              <div class="alert-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-message">
                  {{ alert.message }}
                </div>
                <div class="alert-meta">
                  <el-tag
                    size="small"
                    type="warning"
                  >
                    Warning
                  </el-tag>
                  <span class="alert-time">{{ formatTime(alert.createdAt) }}</span>
                </div>
              </div>
            </div>

            <el-empty
              v-if="warningAlerts.length === 0"
              description="No warnings"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

interface Alert {
  id: string
  type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  createdAt: string
  read: boolean
  actionable?: boolean
  actionType?: string
  actionData?: any
}

const loading = ref(false)
const activeTab = ref('all')
const alerts = ref<Alert[]>([])

const allAlerts = computed(() => alerts.value)
const criticalAlerts = computed(() => alerts.value.filter((a) => a.severity === 'critical'))
const warningAlerts = computed(() => alerts.value.filter((a) => a.severity === 'high' || a.severity === 'medium'))
const unreadCount = computed(() => alerts.value.filter((a) => !a.read).length)

const alertIcons: Record<string, any> = {
  critical: 'CircleCloseFilled',
  high: 'WarningFilled',
  medium: 'InfoFilled',
  low: 'Notification',
}

async function fetchAlerts() {
  loading.value = true

  try {
    // Mock data - replace with API call
    alerts.value = [
      {
        id: '1',
        type: 'workflow_failed',
        severity: 'critical',
        message: 'Workflow "Daily Outreach" failed: Rate limit exceeded',
        createdAt: dayjs().subtract(5, 'minutes').toISOString(),
        read: false,
        actionable: true,
        actionType: 'takeover',
      },
      {
        id: '2',
        type: 'takeover_needed',
        severity: 'high',
        message: 'High intent conversation requires attention: @retailer456',
        createdAt: dayjs().subtract(15, 'minutes').toISOString(),
        read: false,
        actionable: true,
        actionType: 'takeover',
      },
      {
        id: '3',
        type: 'low_open_rate',
        severity: 'medium',
        message: 'Email open rate is below threshold (15%)',
        createdAt: dayjs().subtract(1, 'hour').toISOString(),
        read: true,
      },
      {
        id: '4',
        type: 'high_intent_leads',
        severity: 'medium',
        message: '3 high intent leads need attention',
        createdAt: dayjs().subtract(2, 'hours').toISOString(),
        read: true,
      },
      {
        id: '5',
        type: 'account_warning',
        severity: 'low',
        message: 'Gmail account approaching daily limit (85/100)',
        createdAt: dayjs().subtract(3, 'hours').toISOString(),
        read: true,
      },
    ]
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
  } finally {
    loading.value = false
  }
}

function markAllRead() {
  alerts.value.forEach((a) => (a.read = true))
  ElMessage.success('All alerts marked as read')
}

function dismissAlert(id: string) {
  alerts.value = alerts.value.filter((a) => a.id !== id)
  ElMessage.info('Alert dismissed')
}

function handleAlert(alert: Alert) {
  if (alert.actionable) {
    if (alert.actionType === 'takeover') {
      // Navigate to conversation
      ElMessage.info(`Taking action on ${alert.type}`)
    }
  }
}

function getAlertIcon(severity: string) {
  return alertIcons[severity] || 'Notification'
}

function getAlertType(severity: string) {
  const types: Record<string, any> = {
    critical: 'danger',
    high: 'warning',
    medium: 'warning',
    low: 'info',
  }
  return types[severity] || 'info'
}

function formatTime(time: string) {
  return dayjs(time).fromNow()
}

onMounted(() => {
  fetchAlerts()
})
</script>

<style lang="scss" scoped>
.alert-panel {
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-content {
  min-height: 350px;
}

.alerts-list {
  max-height: 400px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  background: var(--el-fill-color-blank);
  border: 1px solid var(--el-border-color-light);
  transition: all 0.2s;

  &:hover {
    background: var(--el-fill-color-light);
  }

  &.unread {
    border-left: 3px solid var(--el-color-primary);
  }

  &.alert-critical {
    background: rgba(245, 108, 108, 0.05);
    border-color: rgba(245, 108, 108, 0.3);
  }
}

.alert-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.alert-item {
  &.alert-critical .alert-icon {
    background: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }

  &.alert-high .alert-icon {
    background: var(--el-color-warning-light-9);
    color: var(--el-color-warning);
  }

  &.alert-medium .alert-icon {
    background: var(--el-color-info-light-9);
    color: var(--el-color-info);
  }
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-message {
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.alert-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.alert-time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.alert-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}
</style>
