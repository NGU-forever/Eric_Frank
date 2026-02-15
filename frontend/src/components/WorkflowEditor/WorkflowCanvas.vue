<template>
  <div class="workflow-canvas">
    <div
      ref="canvasRef"
      class="canvas-container"
      :class="{ 'drag-over': isDragOver }"
      @drop="onDrop"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
    >
      <div
        v-if="steps.length === 0"
        class="empty-placeholder"
      >
        <el-icon size="48">
          <Connection />
        </el-icon>
        <p>Drag skills here to build your workflow</p>
      </div>

      <div
        v-else
        class="workflow-nodes"
      >
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="workflow-node"
          :style="{ left: step.x + 'px', top: step.y + 'px' }"
          @mousedown="startDrag($event, step)"
        >
          <div
            class="node-header"
            :class="{ 'selected': selectedStep?.id === step.id }"
          >
            <el-icon><Operation /></el-icon>
            <span class="node-title">{{ step.name }}</span>
            <el-button
              text
              type="danger"
              size="small"
              @click.stop="removeStep(step.id)"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>

          <div class="node-body">
            <el-tag size="small">
              {{ step.skillName }}
            </el-tag>
            <div
              v-if="step.config && Object.keys(step.config).length > 0"
              class="config-badge"
            >
              <el-icon><Setting /></el-icon>
              <span>{{ Object.keys(step.config).length }}</span>
            </div>
          </div>

          <!-- Connection points -->
          <div
            class="connection-point input"
            @click.stop="showConnections(step.id, 'input')"
          />
          <div
            class="connection-point output"
            @click.stop="showConnections(step.id, 'output')"
          />
        </div>

        <!-- Connection lines -->
        <svg class="connections-layer">
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="10"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="#409eff"
              />
            </marker>
          </defs>
          <line
            v-for="connection in connections"
            :key="connection.id"
            :x1="connection.x1"
            :y1="connection.y1"
            :x2="connection.x2"
            :y2="connection.y2"
            stroke="#409eff"
            stroke-width="2"
            marker-end="url(#arrowhead)"
            :class="{ 'selected': selectedConnection?.id === connection.id }"
            @click.stop="selectConnection(connection.id)"
          />
        </svg>
      </div>
    </div>

    <!-- Zoom controls -->
    <div class="zoom-controls">
      <el-button-group>
        <el-button
          size="small"
          @click="zoomOut"
        >
          <el-icon><ZoomOut /></el-icon>
        </el-button>
        <el-button
          size="small"
          disabled
        >
          {{ Math.round(zoom * 100) }}%
        </el-button>
        <el-button
          size="small"
          @click="zoomIn"
        >
          <el-icon><ZoomIn /></el-icon>
        </el-button>
      </el-button-group>
    </div>

    <!-- Node properties panel -->
    <el-drawer
      v-model="showProperties"
      direction="right"
      size="350px"
    >
      <template #header>
        <div class="properties-header">
          <span>Node Properties</span>
          <el-button
            text
            @click="showProperties = false"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </template>

      <div
        v-if="selectedStep"
        class="properties-content"
      >
        <el-form
          :model="selectedStep"
          label-position="top"
        >
          <el-form-item label="Step Name">
            <el-input
              v-model="selectedStep.name"
              @change="updateStep"
            />
          </el-form-item>

          <el-form-item label="Skill">
            <el-select
              v-model="selectedStep.skillName"
              @change="updateStep"
            >
              <el-option
                v-for="skill in skills"
                :key="skill.name"
                :label="skill.display_name"
                :value="skill.name"
              />
            </el-select>
          </el-form-item>

          <el-divider />

          <h4>Configuration</h4>
          <el-form-item label="Retry on Failure">
            <el-switch
              v-model="selectedStep.retryOnFailure"
              @change="updateStep"
            />
          </el-form-item>

          <el-form-item label="Max Retries">
            <el-input-number
              v-model="selectedStep.maxRetries"
              :min="0"
              :max="10"
              @change="updateStep"
            />
          </el-form-item>

          <el-form-item label="Timeout (seconds)">
            <el-input-number
              v-model="selectedStep.timeout"
              :min="1"
              :max="3600"
              @change="updateStep"
            />
          </el-form-item>

          <el-form-item label="On Failure">
            <el-select
              v-model="selectedStep.onFailureAction"
              @change="updateStep"
            >
              <el-option
                label="Skip"
                value="skip"
              />
              <el-option
                label="Stop"
                value="stop"
              />
              <el-option
                label="Continue"
                value="continue"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Condition">
            <el-select
              v-model="selectedStep.condition"
              @change="updateStep"
            >
              <el-option
                label="Always"
                value="always"
              />
              <el-option
                label="On Success"
                value="on_success"
              />
              <el-option
                label="On Failure"
                value="on_failure"
              />
              <el-option
                label="On Skip"
                value="on_skip"
              />
              <el-option
                label="Custom"
                value="custom"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            v-if="selectedStep.condition === 'custom'"
            label="Condition Expression"
          >
            <el-input
              v-model="selectedStep.conditionExpression"
              type="textarea"
              placeholder="e.g., state.intent_level == 'high'"
              @change="updateStep"
            />
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>

    <!-- Skill palette -->
    <div class="skill-palette">
      <div class="palette-header">
        Skills
      </div>
      <div class="palette-content">
        <div
          v-for="skill in skills"
          :key="skill.name"
          class="skill-item"
          draggable="true"
          @dragstart="onSkillDragStart($event, skill)"
        >
          <div class="skill-icon">
            <el-icon><Operation /></el-icon>
          </div>
          <div class="skill-info">
            <span class="skill-name">{{ skill.display_name }}</span>
            <span class="skill-category">{{ skill.category }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { Skill, WorkflowStep } from '@/types'

interface Props {
  modelValue?: WorkflowStep[]
  connections?: any[]
  skills?: Skill[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  connections: () => [],
  skills: () => [],
})

const emit = defineEmits<{
  'update:modelValue': [value: WorkflowStep[]]
  'update:connections': [value: any[]]
  'save': []
}>()

// Refs
const canvasRef = ref<HTMLElement>()
const isDragOver = ref(false)
const showProperties = ref(false)
const selectedStep = ref<WorkflowStep | null>(null)
const selectedConnection = ref<any | null>(null)
const zoom = ref(1)

// Computed
const steps = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Node dragging
let draggingNode: WorkflowStep | null = null
let dragOffset = { x: 0, y: 0 }

function onDragOver(event: DragEvent) {
  event.preventDefault()
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  isDragOver.value = false

  // Handle skill drop
  const skillData = event.dataTransfer?.getData('application/json')
  if (skillData) {
    addNode(event, skillData)
  }
}

function onSkillDragStart(event: DragEvent, skill: Skill) {
  event.dataTransfer?.setData('application/json', JSON.stringify(skill))
}

function addNode(event: DragEvent, skill: Skill) {
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  const canvasRect = canvasRef.value?.getBoundingClientRect()

  const x = event.clientX - (canvasRect?.left || 0)
  const y = event.clientY - (canvasRect?.top || 0)

  const newNode: WorkflowStep = {
    id: `step_${Date.now()}`,
    name: `${skill.display_name} ${steps.value.length + 1}`,
    skillName: skill.name,
    skillDisplayName: skill.display_name,
    x: x - 75,
    y: y - 30,
    config: {},
    retryOnFailure: true,
    maxRetries: 3,
    timeout: 300,
    condition: 'always',
    onFailureAction: 'skip',
  }

  steps.value = [...steps.value, newNode]
}

function startDrag(event: MouseEvent, step: WorkflowStep) {
  draggingNode = step
  dragOffset = {
    x: event.clientX - step.x,
    y: event.clientY - step.y
  }

  document.addEventListener('mousemove', onNodeDrag)
  document.addEventListener('mouseup', stopNodeDrag)

  // Select node
  selectedStep.value = step
  showProperties.value = true
}

function onNodeDrag(event: MouseEvent) {
  if (!draggingNode) return

  const newX = event.clientX - dragOffset.x
  const newY = event.clientY - dragOffset.y

  // Update node position
  const index = steps.value.findIndex(s => s.id === draggingNode!.id)
  if (index !== -1) {
    steps.value[index].x = newX
    steps.value[index].y = newY
  }
}

function stopNodeDrag() {
  draggingNode = null
  document.removeEventListener('mousemove', onNodeDrag)
  document.removeEventListener('mouseup', stopNodeDrag)
}

function removeStep(id: string) {
  steps.value = steps.value.filter(s => s.id !== id)

  // Also remove connections
  const updatedConnections = props.connections.filter(
    c => c.from !== id && c.to !== id
  )
  emit('update:connections', updatedConnections)

  if (selectedStep.value?.id === id) {
    selectedStep.value = null
    showProperties.value = false
  }
}

function selectNode(id: string) {
  selectedStep.value = steps.value.find(s => s.id === id) || null
  if (selectedStep.value) {
    showProperties.value = true
  }
}

function selectConnection(id: string) {
  selectedConnection.value = props.connections.find(c => c.id === id) || null
}

function showConnections(stepId: string, type: string) {
  // Show connection options
  ElMessage.info('Connection mode: click on another node to connect')
}

function updateStep() {
  if (selectedStep.value) {
    const index = steps.value.findIndex(s => s.id === selectedStep.value!.id)
    if (index !== -1) {
      steps.value[index] = { ...selectedStep.value }
    }
  }
}

function zoomIn() {
  if (zoom.value < 2) {
    zoom.value += 0.1
  }
}

function zoomOut() {
  if (zoom.value > 0.5) {
    zoom.value -= 0.1
  }
}

// Keyboard shortcuts
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Delete' && selectedStep.value) {
    removeStep(selectedStep.value.id)
  }
  if (event.key === 'Escape') {
    selectedStep.value = null
    showProperties.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style lang="scss" scoped>
.workflow-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--el-fill-color-lighter);
}

.canvas-container {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform 0.2s;

  &.drag-over {
    background: var(--el-fill-color-light);
  }
}

.empty-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--el-text-color-secondary);

  .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: var(--el-border-color);
  }
}

.workflow-nodes {
  position: relative;
  width: 100%;
  height: 100%;
}

.workflow-node {
  position: absolute;
  width: 200px;
  background: var(--el-bg-color);
  border: 2px solid var(--el-border-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: move;
  user-select: none;
  transition: border-color 0.2s;

  &:hover {
    border-color: var(--el-color-primary);
  }
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-fill-color-light);

  &.selected {
    background: var(--el-color-primary-light-9);
  }
}

.node-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.node-body {
  padding: 12px;
}

.config-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.connection-point {
  position: absolute;
  width: 12px;
  height: 12px;
  background: var(--el-color-primary);
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.5);
  }

  &.input {
    top: 50%;
    left: -6px;
    transform: translateY(-50%);
  }

  &.output {
    top: 50%;
    right: -6px;
    transform: translateY(-50%);
  }
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;

  line {
    pointer-events: stroke;
    cursor: pointer;

    &.selected {
      stroke: var(--el-color-warning);
      stroke-width: 3;
    }
  }
}

.zoom-controls {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: var(--el-bg-color);
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.skill-palette {
  position: absolute;
  left: 0;
  top: 0;
  width: 260px;
  height: 100%;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.palette-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color);
  font-weight: 600;
}

.palette-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.skill-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  margin-bottom: 8px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;

  &:hover {
    border-color: var(--el-color-primary);
    background: var(--el-fill-color-light);
  }
}

.skill-icon {
  width: 32px;
  height: 32px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
}

.skill-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.skill-name {
  font-size: 14px;
  font-weight: 500;
}

.skill-category {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.properties-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.properties-content {
  h4 {
    margin: 20px 0 12px;
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}
</style>
