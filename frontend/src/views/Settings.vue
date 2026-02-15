"""
前端Settings视图页面
"""
<template>
  <div class="settings">
    <h1>Settings</h1>

    <el-row :gutter="20">
      <el-col
        :xs="24"
        :lg="16"
      >
        <!-- General Settings -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>General</span>
            </div>
          </template>

          <el-form
            :model="generalForm"
            label-width="150px"
          >
            <el-form-item label="Application Name">
              <el-input v-model="generalForm.appName" />
            </el-form-item>

            <el-form-item label="Theme">
              <el-radio-group v-model="generalForm.theme">
                <el-radio label="light">
                  Light
                </el-radio>
                <el-radio label="dark">
                  Dark
                </el-radio>
                <el-radio label="auto">
                  Auto
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="Language">
              <el-select v-model="generalForm.language">
                <el-option
                  label="English"
                  value="en"
                />
                <el-option
                  label="中文"
                  value="zh"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Timezone">
              <el-select
                v-model="generalForm.timezone"
                filterable
              >
                <el-option
                  v-for="tz in timezones"
                  :key="tz.value"
                  :label="tz.label"
                  :value="tz.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Date Format">
              <el-select v-model="generalForm.dateFormat">
                <el-option
                  label="YYYY-MM-DD"
                  value="yyyy-MM-dd"
                />
                <el-option
                  label="MM/DD/YYYY"
                  value="MM/dd/yyyy"
                />
                <el-option
                  label="DD/MM/YYYY"
                  value="dd/MM/yyyy"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Notification Settings -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Bell /></el-icon>
              <span>Notifications</span>
            </div>
          </template>

          <el-form
            :model="notificationForm"
            label-width="150px"
          >
            <el-form-item label="Email Notifications">
              <el-switch v-model="notificationForm.email" />
            </el-form-item>

            <el-form-item label="Push Notifications">
              <el-switch v-model="notificationForm.push" />
            </el-form-item>

            <el-form-item label="Browser Notifications">
              <el-switch v-model="notificationForm.browser" />
            </el-form-item>

            <el-divider />

            <el-form-item label="Digest Email">
              <el-switch v-model="notificationForm.digest" />
            </el-form-item>

            <el-form-item label="Digest Schedule">
              <el-select
                v-model="notificationForm.digestSchedule"
                :disabled="!notificationForm.digest"
              >
                <el-option
                  label="Daily"
                  value="daily"
                />
                <el-option
                  label="Weekly"
                  value="weekly"
                />
                <el-option
                  label="Monthly"
                  value="monthly"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col
        :xs="24"
        :lg="8"
      >
        <!-- Account Settings -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><UserFilled /></el-icon>
              <span>Account</span>
            </div>
          </template>

          <div class="account-info">
            <el-avatar :size="80">
              {{ userStore.user?.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="user-details">
              <div class="user-name">
                {{ userStore.user?.fullName || userStore.user?.username }}
              </div>
              <div class="user-email">
                {{ userStore.user?.email }}
              </div>
              <div class="user-role">
                <el-tag :type="userStore.isAdmin ? 'danger' : 'info'">
                  {{ userStore.user?.role?.toUpperCase() }}
                </el-tag>
              </div>
            </div>
          </div>

          <el-divider />

          <el-button
            type="primary"
            @click="showPasswordDialog = true"
          >
            Change Password
          </el-button>
        </el-card>

        <!-- Connected Accounts -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>Connected Accounts</span>
            </div>
          </template>

          <div class="accounts-list">
            <div
              v-for="account in accounts"
              :key="account.id"
              class="account-item"
            >
              <div class="account-icon">
                <el-icon><component :is="getAccountIcon(account.type)" /></el-icon>
              </div>
              <div class="account-info">
                <div class="account-name">
                  {{ account.name }}
                </div>
                <div class="account-email">
                  {{ account.email || account.phone }}
                </div>
              </div>
              <div class="account-status">
                <el-tag
                  :type="account.isVerified ? 'success' : 'info'"
                  size="small"
                >
                  {{ account.isVerified ? 'Verified' : 'Pending' }}
                </el-tag>
              </div>
            </div>

            <el-empty
              v-if="accounts.length === 0"
              description="No connected accounts"
            />
          </div>

          <el-button
            type="primary"
            style="width: 100%"
            @click="showAddAccountDialog = true"
          >
            <el-icon><Plus /></el-icon>
            Add Account
          </el-button>
        </el-card>

        <!-- API Keys -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Key /></el-icon>
              <span>API Keys</span>
            </div>
          </template>

          <div class="api-keys">
            <div
              v-for="provider in apiProviders"
              :key="provider.key"
              class="api-key-item"
            >
              <div class="provider-icon">
                <component :is="provider.icon" />
              </div>
              <div class="provider-info">
                <div class="provider-name">
                  {{ provider.name }}
                </div>
                <div class="provider-status">
                  <el-tag
                    v-if="provider.hasKey"
                    type="success"
                  >
                    Configured
                  </el-tag>
                  <el-tag
                    v-else
                    type="info"
                  >
                    Not Configured
                  </el-tag>
                </div>
              </div>
              <el-button
                text
                @click="configureProvider(provider.key)"
              >
                {{ provider.hasKey ? 'Update' : 'Configure' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Change Password Dialog -->
    <el-dialog
      v-model="showPasswordDialog"
      title="Change Password"
      width="400px"
    >
      <el-form
        :model="passwordForm"
        label-width="120px"
      >
        <el-form-item label="Current Password">
          <el-input
            v-model="passwordForm.current"
            type="password"
          />
        </el-form-item>
        <el-form-item label="New Password">
          <el-input
            v-model="passwordForm.new"
            type="password"
          />
        </el-form-item>
        <el-form-item label="Confirm Password">
          <el-input
            v-model="passwordForm.confirm"
            type="password"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">
          Cancel
        </el-button>
        <el-button
          type="primary"
          @click="changePassword"
        >
          Save
        </el-button>
      </template>
    </el-dialog>

    <!-- Add Account Dialog -->
    <el-dialog
      v-model="showAddAccountDialog"
      title="Add Account"
      width="500px"
    >
      <el-form
        :model="accountForm"
        label-width="120px"
      >
        <el-form-item label="Account Type">
          <el-select v-model="accountForm.type">
            <el-option
              label="Gmail"
              value="gmail"
            />
            <el-option
              label="Outlook"
              value="outlook"
            />
            <el-option
              label="SMTP"
              value="smtp"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Account Name">
          <el-input v-model="accountForm.name" />
        </el-form-item>
        <el-form-item
          v-if="accountForm.type !== 'whatsapp'"
          label="Email"
        >
          <el-input v-model="accountForm.email" />
        </el-form-item>
        <el-form-item
          v-if="accountForm.type === 'whatsapp'"
          label="Phone"
        >
          <el-input v-model="accountForm.phone" />
        </el-form-item>
        <el-form-item label="App Password">
          <el-input
            v-model="accountForm.password"
            type="password"
          />
        </el-form-item>
        <el-form-item label="Daily Limit">
          <el-input-number
            v-model="accountForm.dailyLimit"
            :min="10"
            :max="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAccountDialog = false">
          Cancel
        </el-button>
        <el-button
          type="primary"
          @click="addAccount"
        >
          Add
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore, useThemeStore } from '@/stores'

const userStore = useAuthStore()
const themeStore = useThemeStore()

// Dialog states
const showPasswordDialog = ref(false)
const showAddAccountDialog = ref(false)

// Forms
const generalForm = reactive({
  appName: 'Trade AI Agent',
  theme: 'light',
  language: 'en',
  timezone: 'UTC',
  dateFormat: 'yyyy-MM-dd',
})

const notificationForm = reactive({
  email: true,
  push: false,
  browser: false,
  digest: true,
  digestSchedule: 'daily',
})

const passwordForm = reactive({
  current: '',
  new: '',
  confirm: '',
})

const accountForm = reactive({
  type: 'gmail',
  name: '',
  email: '',
  phone: '',
  password: '',
  dailyLimit: 100,
})

// Data
const timezones = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
  { value: 'Europe/London', label: 'Greenwich Mean Time' },
  { value: 'Europe/Paris', label: 'Central European Time' },
  { value: 'Asia/Shanghai', label: 'China Standard Time' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time' },
  { value: 'Australia/Sydney', label: 'Australian Eastern Time' },
]

const accounts = ref([
  { id: 1, type: 'gmail', name: 'Work Email', email: 'work@company.com', isVerified: true },
  { id: 2, type: 'outlook', name: 'Personal', email: 'personal@outlook.com', isVerified: true },
])

const apiProviders = ref([
  { key: 'tongyi', name: 'Tongyi Qwen', icon: 'MagicStick', hasKey: false },
  { key: 'qwen', name: 'Qwen', icon: 'Grid', hasKey: false },
  { key: 'openai', name: 'OpenAI', icon: 'ChatDotRound', hasKey: false },
])

// Methods
function changeTheme(theme: string) {
  themeStore.setTheme(theme === 'auto' ? 'auto' : theme === 'dark')
}

async function changePassword() {
  if (passwordForm.new !== passwordForm.confirm) {
    ElMessage.error('Passwords do not match')
    return
  }

  try {
    // Call API to change password
    ElMessage.success('Password changed successfully')
    showPasswordDialog.value = false
    passwordForm.current = ''
    passwordForm.new = ''
    passwordForm.confirm = ''
  } catch {
    ElMessage.error('Failed to change password')
  }
}

async function addAccount() {
  try {
    // Call API to add account
    ElMessage.success('Account added successfully')
    showAddAccountDialog.value = false
  } catch {
    ElMessage.error('Failed to add account')
  }
}

function configureProvider(provider: string) {
  ElMessage.info(`Configure ${provider} API key`)
}

function getAccountIcon(type: string) {
  const icons: Record<string, any> = {
    gmail: 'Message',
    outlook: 'Message',
    smtp: 'Message',
    whatsapp: 'ChatDotRound',
  }
  return icons[type] || 'Link'
}
</script>

<style lang="scss" scoped>
.settings {
  h1 {
    margin-bottom: 20px;
  }
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.account-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid var(--el-border-color-light);
}

.user-details {
  text-align: center;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.account-list {
  max-height: 300px;
  overflow-y: auto;
}

.account-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
}

.account-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--el-bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
  font-size: 18px;
}

.account-info {
  flex: 1;
  min-width: 0;
}

.account-name {
  font-size: 14px;
  font-weight: 500;
}

.account-email {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.api-keys {
  max-height: 300px;
  overflow-y: auto;
}

.api-key-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);
}

.provider-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
  font-size: 20px;
}

.provider-info {
  flex: 1;
}

.provider-name {
  font-size: 14px;
  font-weight: 500;
}

.provider-status {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
