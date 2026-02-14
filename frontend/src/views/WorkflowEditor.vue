<template>
  <div class="workflow-editor">
    <WorkflowToolbar
      @save="onSave"
      @execute="onExecute"
      @export="onExport"
    />

    <div class="editor-layout">
      <WorkflowCanvas
        v-model="workflowSteps"
        v-model:connections="connections"
        :skills="skills"
        @update:connections="onUpdateConnections"
        @node-click="onNodeClick"
      />

      <!-- WorkflowEditor右侧面板 -->
      <div class="editor-panel">
        <el-card class="properties-card">
          <template #header>
            <span>Workflow Properties</span>
          </template>

          <el-form
            :model="workflowForm"
            label-position="top"
          >
            <el-form-item label="Workflow Name">
              <el-input
                v-model="workflowForm.name"
                @change="updateWorkflowName"
              />
            </el-form-item>

            <el-form-item label="Description">
              <el-input
                v-model="workflowForm.description"
                type="textarea"
                placeholder="Describe this workflow..."
                @change="updateWorkflowDescription"
              />
            </el-form-item>

            <el-form-item label="Tags">
              <el-select
                v-model="workflowForm.tags"
                multiple
                filterable
                allow-create
                placeholder="Add tags..."
                @change="updateWorkflowTags"
              >
                <el-option
                  v-for="tag in availableTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>

            <el-divider />

            <h4>Execution Settings</h4>
            <el-form-item label="Timeout (seconds)">
              <el-input-number
                v-model="workflowForm.timeout"
                :min="1"
                :max="3600"
              />
            </el-form-item>

            <el-form-item label="Retry Strategy">
              <el-radio-group v-model="workflowForm.retryStrategy">
                <el-radio label="linear">
                  Linear
                </el-radio>
                <el-radio label="exponential">
                  Exponential
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="Max Retries">
              <el-input-number
                v-model="workflowForm.maxRetries"
                :min="0"
                :max="10"
              />
            </el-form-item>

            <el-divider />

            <div class="action-buttons">
              <el-button @click="validateWorkflow">
                <el-icon><CircleCheck /></el-icon>
                Validate
              </el-button>
              <el-button @click="resetWorkflow">
                <el-icon><RefreshLeft /></el-icon>
                Reset
              </el-button>
            </div>
          </el-form>
        </el-card>
      </div>
    </div>

    <!-- Execution Panel -->
    <el-dialog
      v-model="showExecutionPanel"
      title="Execution Progress"
      width="700px"
      :close-on-click-modal="false"
    >
      <ExecutionProgress
        :execution="currentExecution"
        @pause="onPauseExecution"
        @resume="onResumeExecution"
        @cancel="onCancelExecution"
        @view-details="onViewExecutionDetails"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import WorkflowToolbar from '@/components/WorkflowEditor/WorkflowToolbar.vue'
import WorkflowCanvas from '@/components/WorkflowEditor/WorkflowCanvas.vue'
import ExecutionProgress from '@/components/Monitor/ExecutionMonitor.vue'
import type { Skill, WorkflowStep } from '@/types'
import { workflowApi } from '@/api/workflow'
import { skillApi } from '@/api/skill'

const route = useRoute()
const router = useRouter()

// Workflow form
const workflowForm = reactive({
  name: 'New Workflow',
  description: '',
  tags: [],
  timeout: 300,
  retryStrategy: 'linear',
  maxRetries: 3,
})

// Workflow data
const workflowSteps = ref<WorkflowStep[]>([])
const connections = ref<any[]>([])

const availableTags = ref([
  'outreach',
  'lead_generation',
  'customer_engagement',
  'follow_up',
  'nurturing',
])

const skills = ref<Skill[]>([])
const currentExecution = ref<any>(null)
const showExecutionPanel = ref(false)

const workflowId = computed(() => route.params.id as string)

async function loadWorkflow() {
  try {
    if (workflowId.value) {
      const workflow = await workflowApi.get(workflowId)
      workflowForm.name = workflow.name
      workflowForm.description = workflow.description
      workflowForm.tags = workflow.tags || []

      // Parse steps from config
      const config = workflow.config_json
      if (config && config.steps) {
        workflowSteps.value = config.steps.map((s: any) => ({
          id: s.id,
          name: s.name,
          skillName: s.skill_name,
          skillDisplayName: s.skill_display_name,
          x: s.x || 100,
          y: s.y || 50,
          config: s.config || {},
          retryOnFailure: s.retry_on_failure ?? true,
          maxRetries: s.max_retries || 3,
          timeout: s.timeout || 300,
          condition: s.condition || 'always',
          conditionExpression: s.condition_expression,
          onFailureAction: s.on_failure_action || 'skip',
        }))
      }

      if (config && config.connections) {
        connections.value = config.connections
      }
    }
  } catch (error) {
    console.error('Failed to load workflow:', error)
    ElMessage.error('Failed to load workflow')
  }
}

async function loadSkills() {
  try {
    const response = await skillApi.list()
    // Transform API response to match Skill type
    skills.value = response.skills.map((s: any) => ({
      id: s.name,
      name: s.name,
      displayName: s.display_name,
      description: s.description,
      category: s.category,
      inputSchema: s.input_schema,
      outputSchema: s.output_schema,
      configTemplate: s.config_schema,
      icon: s.icon,
      version: s.version,
      enabled: true,
    }))
  } catch (error) {
    console.error('Failed to load skills:', error)
  }
}

function onSave() {
  // Save workflow
  const workflowData = {
    name: workflowForm.name,
    description: workflowForm.description,
    steps: workflowSteps.value.map((s) => ({
      name: s.name,
      skill_name: s.skillName,
      config: s.config,
      condition: s.condition,
      condition_expression: s.conditionExpression,
      retry_on_failure: s.retryOnFailure,
      max_retries: s.maxRetries,
      timeout: s.timeout,
      on_failure_action: s.onFailureAction,
    })),
    transitions: connections.value,
    tags: workflowForm.tags,
    timeout: workflowForm.timeout,
    retry_strategy: workflowForm.retryStrategy,
    max_retries: workflowForm.maxRetries,
  }

  console.log('Saving workflow:', workflowData)
  ElMessage.success('Workflow saved successfully')
}

async function onExecute() {
  try {
    await workflowApi.execute(workflowId, {})
    showExecutionPanel.value = true
    currentExecution.value = {
      id: `exec_${Date.now()}`,
      workflow_name: workflowForm.name,
      status: 'running',
      progress: 0,
    }
  } catch (error) {
    console.error('Failed to execute workflow:', error)
    ElMessage.error('Failed to execute workflow')
  }
}

function onExport() {
  const workflowData = {
    name: workflowForm.name,
    description: workflowForm.description,
    steps: workflowSteps.value,
    connections: connections.value,
    tags: workflowForm.tags,
  }

  const blob = new Blob([JSON.stringify(workflowData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = `${workflowForm.name}.json`
  link.click()

  URL.revokeObjectURL(url)
  ElMessage.success('Workflow exported')
}

function onUpdateConnections(newConnections: any[]) {
  connections.value = newConnections
}

function onNodeClick(stepId: string) {
  // Handle node click - could show properties panel
}

function updateWorkflowName() {
  // Update workflow name
}

function updateWorkflowDescription() {
  // Update workflow description
}

function updateWorkflowTags() {
  // Update workflow tags
}

function validateWorkflow() {
  // Validate workflow structure
  const errors: string[] = []

  if (workflowSteps.value.length === 0) {
    errors.push('Add at least one step to the workflow')
  }

  if (!errors.length) {
    ElMessage.success('Workflow is valid')
  } else {
    ElMessage.error('Workflow validation failed', errors.join(', '))
  }
}

function resetWorkflow() {
  workflowSteps.value = []
  connections.value = []
  workflowForm.name = 'New Workflow'
  workflowForm.description = ''
  workflowForm.tags = []
  ElMessage.info('Workflow reset')
}

function onPauseExecution() {
  // Pause execution
}

function onResumeExecution() {
  // Resume execution
}

function onCancelExecution() {
  // Cancel execution
  showExecutionPanel.value = false
}

function onViewExecutionDetails() {
  // View execution details
}

onMounted(() => {
  loadWorkflow()
  loadSkills()
})
</script>

<style lang="scss" scoped>
.workflow-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
}

.editor-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.editor-panel {
  width: 350px;
  padding: 16px;
  border-left: 1px solid var(--el-border-color);
  background: var(--el-bg-color-page);
}

.properties-card {
  :deep(.el-card__body) {
    padding: 20px;
  }

  h4 {
    margin: 20px 0 12px;
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }

  .action-buttons {
    display: flex;
    gap: 8px;
    margin-top: 20px;
  }
}
</style>
