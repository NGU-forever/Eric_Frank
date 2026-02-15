<template>
  <el-container class="main-layout">
    <el-aside
      width="250px"
      class="sidebar"
    >
      <div class="logo">
        <h2>Trade AI Agent</h2>
      </div>

      <el-menu
        :default-active="activeMenu"
        :router="true"
        class="sidebar-menu"
        :collapse="isCollapsed"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>
            Dashboard
          </template>
        </el-menu-item>

        <el-menu-item index="/workflows">
          <el-icon><Operation /></el-icon>
          <template #title>
            Workflows
          </template>
        </el-menu-item>

        <el-menu-item index="/customers">
          <el-icon><User /></el-icon>
          <template #title>
            Customers
          </template>
        </el-menu-item>

        <el-menu-item index="/conversations">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>
            Conversations
          </template>
        </el-menu-item>

        <el-menu-item index="/analytics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>
            Analytics
          </template>
        </el-menu-item>

        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>
            Settings
          </template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-content">
      <el-header class="header">
        <div class="header-left">
          <el-button
            text
            @click="toggleCollapse"
          >
            <el-icon><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
          </el-button>
        </div>

        <div class="header-right">
          <el-switch
            v-model="isDark"
            inline-prompt
            style="--el-switch-on-color: #409eff"
            active-text="🌙"
            inactive-text="☀️"
            @change="toggleTheme"
          />

          <el-dropdown trigger="click">
            <div class="user-avatar">
              <el-avatar :size="32">
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>Profile</el-dropdown-item>
                <el-dropdown-item
                  divided
                  @click="logout"
                >
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isCollapsed = ref(false)
const isDark = computed({
  get: () => themeStore.isDark,
  set: (val) => themeStore.setTheme(val),
})

const activeMenu = computed(() => route.path)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

function toggleTheme() {
  themeStore.toggleTheme()
}

async function logout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background: var(--el-bg-color-page);
  border-right: 1px solid var(--el-border-color);

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid var(--el-border-color);

    h2 {
      font-size: 18px;
      font-weight: 600;
    }
  }

  .sidebar-menu {
    border: none;
  }
}

.main-content {
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid var(--el-border-color);
  background: var(--el-bg-color);

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .user-avatar {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;

    .username {
      font-size: 14px;
    }
  }
}
</style>
