<template>
  <div class="workflows">
    <div class="page-header">
      <h1>Workflows</h1>
      <el-button
        type="primary"
        @click="showCreateDialog = true"
      >
        <el-icon><Plus /></el-icon>
        Create Workflow
      </el-button>
    </div>

    <el-card>
      <el-table
        v-loading="loading"
        :data="workflows"
      >
        <el-table-column
          prop="name"
          label="Name"
        />
        <el-table-column
          prop="description"
          label="Description"
          show-overflow-tooltip
        />
        <el-table-column
          prop="status"
          label="Status"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="version"
          label="Version"
          width="100"
        />
        <el-table-column
          label="Actions"
          width="200"
        >
          <template #default="{ row }">
            <el-button
              text
              @click="editWorkflow(row.id)"
            >
              Edit
            </el-button>
            <el-button
              text
              @click="executeWorkflow(row.id)"
            >
              Execute
            </el-button>
            <el-button
              text
              type="danger"
              @click="deleteWorkflow(row.id)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="showCreateDialog"
      title="Create Workflow"
      width="600px"
    >
      <el-form
        :model="form"
        label-position="top"
      >
        <el-form-item label="Name">
          <el-input
            v-model="form.name"
            placeholder="Enter workflow name"
          />
        </el-form-item>
        <el-form-item label="Description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="Enter workflow description"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">
          Cancel
        </el-button>
        <el-button
          type="primary"
          @click="createWorkflow"
        >
          Create
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useWorkflowStore } from '@/stores/workflow'

const router = useRouter()
const workflowStore = useWorkflowStore()

const loading = ref(false)
const showCreateDialog = ref(false)
const workflows = ref<any[]>([])

const form = ref({
  name: '',
  description: '',
})

async function fetchWorkflows() {
  loading.value = true
  try {
    await workflowStore.fetchWorkflows()
    workflows.value = workflowStore.workflows
  } finally {
    loading.value = false
  }
}

async function createWorkflow() {
  try {
    await workflowStore.createWorkflow({
      name: form.value.name,
      description: form.value.description,
      steps: [],
      transitions: [],
    })
    ElMessage.success('Workflow created')
    showCreateDialog.value = false
    form.value = { name: '', description: '' }
    await fetchWorkflows()
  } catch {
    ElMessage.error('Failed to create workflow')
  }
}

function editWorkflow(id: string) {
  router.push(`/workflows/${id}`)
}

async function executeWorkflow(id: string) {
  try {
    await ElMessageBox.confirm('Execute this workflow?', 'Confirm')
    await workflowStore.executeWorkflow(id, {})
    ElMessage.success('Workflow execution started')
  } catch {
    // Cancelled
  }
}

async function deleteWorkflow(id: string) {
  try {
    await ElMessageBox.confirm('Delete this workflow?', 'Confirm', {
      type: 'warning',
    })
    await workflowStore.deleteWorkflow(id)
    ElMessage.success('Workflow deleted')
    await fetchWorkflows()
  } catch {
    // Cancelled
  }
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    active: 'success',
    paused: 'warning',
    draft: 'info',
    archived: 'info',
  }
  return types[status] || 'info'
}

onMounted(() => {
  fetchWorkflows()
})
</script>

<style lang="scss" scoped>
.workflows {
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;

    h1 {
      margin: 0;
    }
  }
}
</style>
