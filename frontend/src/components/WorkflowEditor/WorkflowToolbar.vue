<template>
  <div class="workflow-toolbar">
    <el-space>
      <el-button
        :disabled="!canUndo"
        @click="onUndo"
      >
        <el-icon><RefreshLeft /></el-icon>
        Undo
      </el-button>

      <el-button
        :disabled="!canRedo"
        @click="onRedo"
      >
        <el-icon><RefreshRight /></el-icon>
        Redo
      </el-button>

      <el-divider direction="vertical" />

      <el-button
        type="primary"
        @click="onSave"
      >
        <el-icon><DocumentChecked /></el-icon>
        Save
      </el-button>

      <el-button @click="onExecute">
        <el-icon><VideoPlay /></el-icon>
        Execute
      </el-button>

      <el-button @click="onExport">
        <el-icon><Download /></el-icon>
        Export
      </el-button>

      <el-divider direction="vertical" />

      <el-button @click="onZoomIn">
        <el-icon><ZoomIn /></el-icon>
      </el-button>

      <el-button @click="onZoomOut">
        <el-icon><ZoomOut /></el-icon>
      </el-button>

      <el-button @click="onZoomFit">
        <el-icon><FullScreen /></el-icon>
        Fit
      </el-button>

      <el-divider direction="vertical" />

      <el-dropdown trigger="click">
        <el-button>
          <el-icon><MoreFilled /></el-icon>
          More
          <el-icon class="el-icon--right">
            <ArrowDown />
          </el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="onClear">
              <el-icon><Delete /></el-icon>
              Clear Canvas
            </el-dropdown-item>
            <el-dropdown-item @click="onValidate">
              <el-icon><CircleCheck /></el-icon>
              Validate Workflow
            </el-dropdown-item>
            <el-dropdown-item
              divided
              @click="onShowLogs"
            >
              <el-icon><Document /></el-icon>
              View Logs
            </el-dropdown-item>
            <el-dropdown-item @click="onShowSettings">
              <el-icon><Setting /></el-icon>
              Settings
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-badge
        :value="errorsCount"
        :hidden="errorsCount === 0"
        type="danger"
      >
        <el-button type="warning">
          <el-icon><Warning /></el-icon>
        </el-button>
      </el-badge>
    </el-space>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'

const emit = defineEmits<{
  undo: []
  redo: []
  save: []
  execute: []
  export: []
  zoomIn: []
  zoomOut: []
  zoomFit: []
  clear: []
  validate: []
  showLogs: []
  showSettings: []
}>()

const historyStack = ref<any[]>([])
const redoStack = ref<any[]>([])
const errorsCount = ref(0)

const canUndo = computed(() => historyStack.value.length > 1)
const canRedo = computed(() => redoStack.value.length > 0)

function onUndo() {
  if (canUndo.value) {
    const currentState = historyStack.value.pop()
    redoStack.value.push(currentState)
    ElMessage.info('Undo')
  }
}

function onRedo() {
  if (canRedo.value) {
    const nextState = redoStack.value.pop()
    historyStack.value.push(nextState)
    ElMessage.info('Redo')
  }
}

function onSave() {
  emit('save')
  ElNotification({
    title: 'Success',
    message: 'Workflow saved successfully',
    type: 'success',
  })
}

function onExecute() {
  emit('execute')
  ElMessage.info('Starting workflow execution...')
}

function onExport() {
  emit('export')
  ElMessage.info('Exporting workflow...')
}

function onZoomIn() {
  emit('zoomIn')
}

function onZoomOut() {
  emit('zoomOut')
}

function onZoomFit() {
  emit('zoomFit')
}

function onClear() {
  ElMessageBox.confirm(
    'This will clear all nodes and connections. Continue?',
    'Clear Workflow',
    {
      confirmButtonText: 'Clear',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(() => {
    emit('clear')
    historyStack.value = []
    redoStack.value = []
    ElMessage.success('Workflow cleared')
  }).catch(() => {})
}

function onValidate() {
  emit('validate')
  errorsCount.value = 0
  ElMessage.info('Validating workflow...')
  // In a real app, this would check for errors
}

function onShowLogs() {
  emit('showLogs')
  ElMessage.info('Opening execution logs...')
}

function onShowSettings() {
  emit('showSettings')
  ElMessage.info('Opening workflow settings...')
}
</script>

<style lang="scss" scoped>
.workflow-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  gap: 12px;
}
</style>
