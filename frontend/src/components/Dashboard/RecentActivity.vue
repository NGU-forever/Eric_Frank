<template>
  <el-card
    class="recent-activity"
    shadow="hover"
  >
    <template #header>
      <div class="card-header">
        <span>Recent Activity</span>
        <el-button
          text
          @click="viewAll"
        >
          View All
        </el-button>
      </div>
    </template>

    <div
      v-loading="loading && props.activities.length === 0"
      class="activity-content"
    >
      <el-timeline v-if="displayActivities.length > 0">
        <el-timeline-item
          v-for="activity in displayActivities"
          :key="activity.id"
          :timestamp="formatTimestamp(activity.timestamp)"
          :type="getActivityType(activity.type)"
        >
          <div class="activity-item">
            <div class="activity-icon">
              <el-icon><component :is="getActivityIcon(activity.type)" /></el-icon>
            </div>
            <div class="activity-detail">
              <div class="activity-description">
                {{ activity.description }}
              </div>
              <div
                v-if="activity.metadata"
                class="activity-meta"
              >
                <el-tag
                  v-for="(value, key) in activity.metadata"
                  :key="key"
                  size="small"
                  type="info"
                >
                  {{ key }}: {{ value }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>

      <el-empty
        v-if="displayActivities.length === 0"
        description="No recent activity"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { api } from '@/api'
import type { ActivityItem } from '@/types'

dayjs.extend(relativeTime)

interface Props {
  activities?: ActivityItem[]
}

const props = withDefaults(defineProps<Props>(), {
  activities: () => [],
})

const router = useRouter()
const loading = ref(false)
const internalActivities = ref<ActivityItem[]>([])

const displayActivities = computed(() => {
  return props.activities.length > 0 ? props.activities : internalActivities.value
})

const activityTypes = {
  message_sent: 'primary',
  message_delivered: 'success',
  message_opened: 'warning',
  reply_received: 'danger',
  workflow_started: 'info',
  workflow_completed: 'success',
  workflow_failed: 'danger',
  customer_created: 'primary',
  customer_updated: 'info',
  takeover_requested: 'warning',
  system_alert: 'danger',
}

const activityIcons: any = {
  message_sent: 'Promotion',
  message_delivered: 'SuccessFilled',
  message_opened: 'View',
  reply_received: 'ChatDotRound',
  workflow_started: 'Operation',
  workflow_completed: 'CircleCheck',
  workflow_failed: 'CircleClose',
  customer_created: 'User',
  customer_updated: 'Edit',
  takeover_requested: 'Warning',
  system_alert: 'WarningFilled',
}

async function fetchActivities() {
  // Only fetch if no activities are provided via props
  if (props.activities.length > 0) return

  loading.value = true

  try {
    // In a real app, this would be an API call
    // const response = await api.get('/api/v1/stats/activities')

    // Mock data for now
    internalActivities.value = [
      {
        id: '1',
        type: 'message_sent',
        description: 'Email sent to @brand123',
        timestamp: dayjs().subtract(5, 'minutes').toISOString(),
      },
      {
        id: '2',
        type: 'reply_received',
        description: 'New reply from @retailer456: "What\'s your pricing?"',
        timestamp: dayjs().subtract(15, 'minutes').toISOString(),
        metadata: { platform: 'email', customer: '@retailer456' },
      },
      {
        id: '3',
        type: 'workflow_completed',
        description: 'Workflow "Lead Generation" completed successfully',
        timestamp: dayjs().subtract(1, 'hour').toISOString(),
        metadata: { workflow: 'Lead Generation', customers: 45 },
      },
      {
        id: '4',
        type: 'customer_created',
        description: '15 new customers imported from TikTok',
        timestamp: dayjs().subtract(2, 'hours').toISOString(),
        metadata: { source: 'TikTok', count: 15 },
      },
      {
        id: '5',
        type: 'message_opened',
        description: 'Email opened by @fashion_brand',
        timestamp: dayjs().subtract(3, 'hours').toISOString(),
      },
    ]
  } catch (error) {
    console.error('Failed to fetch activities:', error)
  } finally {
    loading.value = false
  }
}

function getActivityType(type: string) {
  return activityTypes[type as keyof typeof activityTypes] || 'primary'
}

function getActivityIcon(type: string) {
  return activityIcons[type as keyof typeof activityIcons] || 'Notification'
}

function formatTimestamp(timestamp: string) {
  return dayjs(timestamp).fromNow()
}

function viewAll() {
  router.push('/analytics')
}

onMounted(() => {
  fetchActivities()
})
</script>

<style lang="scss" scoped>
.recent-activity {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
}

.activity-content {
  min-height: 300px;
}

.activity-item {
  display: flex;
  gap: 12px;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
}

.activity-detail {
  flex: 1;
}

.activity-description {
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.5;
}

.activity-meta {
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
