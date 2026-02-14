<template>
  <el-card class="execution-monitor">
    <template #header>
      <div class="monitor-header">
        <div class="monitor-title">
          <el-icon><VideoPlay /></el-icon>
          <span>Execution Monitor</span>
        </div>
        <el-space>
          <el-badge
            :value="activeExecutions"
            type="primary"
          >
            <el-button @click="refresh">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-badge>
          <el-button @click="openSettings">
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-space>
      </div>
    </template>

    <div
      v-loading="loading"
      class="monitor-content"
    >
      <el-table
        :data="executions"
        stripe
      >
        <el-table-column
          prop="workflowName"
          label="Workflow"
          width="200"
        />
        <el-table-column
          prop="status"
          label="Status"
          width="120"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="currentStep"
          label="Current Step"
        />
        <el-table-column
          prop="progress"
          label="Progress"
          width="180"
        >
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :status="getProgressStatus(row.progress, row.status)"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="duration"
          label="Duration"
          width="100"
        />
        <el-table-column
          label="Actions"
          width="200"
          fixed="right"
        >
          <template #default="{ row }">
            <el-space>
              <el-button
                v-if="row.status === 'running'"
                type="warning"
                size="small"
                @click="pauseExecution(row.id)"
              >
                <el-icon><VideoPause /></el-icon>
              </el-button>
              <el-button
                v-if="row.status === 'paused'"
                type="success"
                size="small"
                @click="resumeExecution(row.id)"
              >
                <el-icon><VideoPlay /></el-icon>
              </el-button>
              <el-button
                v-if="row.status !== 'completed' && row.status !== 'cancelled'"
                type="danger"
                size="small"
                @click="cancelExecution(row.id)"
              >
                <el-icon><CircleClose /></el-icon>
              </el-button>
              <el-button
                text
                @click="viewDetails(row.id)"
              >
                <el-icon><View /></el-icon>
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="executions.length === 0"
        description="No active executions"
      />
    </div>

    <!-- Execution Details Dialog -->
    <el-dialog
      v-model="showDetails"
      title="Execution Details"
      width="700px"
    >
      <div v-if="selectedExecution">
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="Execution ID">
            {{ selectedExecution.id }}
          </el-descriptions-item>
          <el-descriptions-item label="Workflow">
            {{ selectedExecution.workflowName }}
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedExecution.status)">
              {{ selectedExecution.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Started At">
            {{ formatTime(selectedExecution.startedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="Finished At">
            {{ formatTime(selectedExecution.finishedAt) }}
          </el-descriptions-item>
          <el-descriptions-item
            label="Current Step"
            :span="2"
          >
            {{ selectedExecution.currentStep || '-' }}
          </el-descriptions-item>
          <el-descriptions-item
            label="Completed Steps"
            :span="2"
          >
            {{ (selectedExecution.completedSteps || []).join(', ') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="selectedExecution.errorMsg"
            label="Error"
            :span="2"
          >
            <el-text type="danger">
              {{ selectedExecution.errorMsg }}
            </el-text>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>Execution Steps</h4>
        <el-timeline>
          <el-timeline-item
            v-for="step in selectedExecution.steps || []"
            :key="step.name"
            :timestamp="step.completedAt"
            :type="getStepStatus(step.status)"
          >
            <div class="step-detail">
              <div class="step-name">
                {{ step.name }}
              </div>
              <div class="step-info">
                <el-tag size="small">
                  {{ step.skillName }}
                </el-tag>
                <span v-if="step.duration">({{ step.duration }})</span>
              </div>
              <div
                v-if="step.error"
                class="step-error"
              >
                <el-text type="danger">
                  {{ step.error }}
                </el-text>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>

      <template #footer>
        <el-button @click="showDetails = false">
          Close
        </el-button>
        <el-button
          type="primary"
          @click="downloadLogs"
        >
          Download Logs
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

interface Execution {
  id: string
  workflowName: string
  status: string
  currentStep: string
  progress: number
  duration: string
  startedAt: string
  finishedAt: string
  completedSteps: string[]
  steps?: any[]
  errorMsg?: string
}

const loading = ref(false)
const executions = ref<Execution[]>([])
const showDetails = ref(false)
const selectedExecution = ref<Execution | null>(null)

const activeExecutions = computed(() =>
  executions.value.filter((e) => e.status === 'running' || e.status === 'paused')
)

async function fetchExecutions() {
  loading.value = true

  try {
    // Mock data - replace with API call
    executions.value = [
      {
        id: 'exec_001',
        workflowName: 'Lead Generation',
        status: 'running',
        currentStep: 'send_messages',
        progress: 65,
        duration: '2m 30s',
        startedAt: dayjs().subtract(2, 'minutes').toISOString(),
        finishedAt: null,
        completedSteps: ['scrape_data', 'clean_data', 'generate_messages'],
        steps: [
          { name: 'scrape_data', skillName: 'Social Scraper', status: 'success', completedAt: dayjs().subtract(2, 'minutes').toISOString() },
          { name: 'clean_data', skillName: 'Data Cleaner', status: 'success', completedAt: dayjs().subtract(1, 'minutes').toISOString() },
          { name: 'generate_messages', skillName: 'Message Generator', status: 'success', completedAt: dayjs().subtract(30, 'seconds').toISOString() },
          { name: 'send_messages', skillName: 'Auto Sender', status: 'running', duration: '30s' },
        ],
      },
      {
        id: 'exec_002',
        workflowName: 'Daily Outreach',
        status: 'paused',
        currentStep: 'send_messages',
        progress: 45,
        duration: '1m 15s',
        startedAt: dayjs().subtract(15, 'minutes').toISOString(),
        finishedAt: null,
        completedSteps: ['load_customers'],
        steps: [
          { name: 'load_customers', skillName: 'Excel Reader', status: 'success', completedAt: dayjs().subtract(15, 'minutes').toISOString() },
          { name: 'send_messages', skillName: 'Auto Sender', status: 'paused', duration: '45s' },
        ],
      },
      {
        id: 'exec_003',
        workflowName: 'Customer Sync',
        status: 'completed',
        currentStep: null,
        progress: 100,
        duration: '45s',
        startedAt: dayjs().subtract(1, 'hour').toISOString(),
        finishedAt: dayjs().subtract(1, 'hour').add(45, 'seconds').toISOString(),
        completedSteps: ['sync_data', 'update_database'],
        steps: [
          { name: 'sync_data', skillName: 'Excel Reader', status: 'success', completedAt: dayjs().subtract(1, 'hour').toISOString() },
          { name: 'update_database', skillName: 'Data Cleaner', status: 'success', completedAt: dayjs().subtract(1, 'hour').add(20, 'seconds').toISOString() },
        ],
      },
    ]
  } catch (error) {
    console.error('Failed to fetch executions:', error)
  } finally {
    loading.value = false
  }
}

function refresh() {
  fetchExecutions()
  ElMessage.info('Refreshing executions...')
}

function openSettings() {
  ElMessage.info('Opening execution settings...')
}

function pauseExecution(id: string) {
  ElMessage.info(`Pausing execution ${id}...`)
}

function resumeExecution(id: string) {
  ElMessage.info(`Resuming execution ${id}...`)
}

async function cancelExecution(id: string) {
  try {
    await ElMessageBox.confirm('Cancel this execution?', 'Confirm', {
      type: 'warning',
    })
    ElMessage.info(`Cancelling execution ${id}...`)
  } catch {
    // Cancelled
  }
}

function viewDetails(id: string) {
  selectedExecution.value = executions.value.find((e) => e.id === id) || null
  showDetails.value = true
}

function downloadLogs() {
  ElMessage.info('Downloading execution logs...')
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    running: 'primary',
    paused: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return types[status] || 'info'
}

function getProgressStatus(progress: number, status: string) {
  if (status === 'failed' || status === 'cancelled') {
    return 'exception'
  }
  if (progress === 100) {
    return 'success'
  }
  return undefined
}

function getStepStatus(status: string) {
  const types: Record<string, any> = {
    success: 'success',
    running: 'primary',
    failed: 'danger',
    skipped: 'info',
  }
  return types[status] || 'info'
}

function formatTime(time?: string) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
}

onMounted(() => {
  fetchExecutions()
})
</script>

<style lang="scss" scoped>
.execution-monitor {
  .monitor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
}

.monitor-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.monitor-content {
  min-height: 400px;
}

.step-detail {
  .step-name {
    font-weight: 500;
    margin-bottom: 4px;
  }

  .step-info {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .step-error {
    margin-top: 4px;
    font-size: 12px;
  }
}
</style>
