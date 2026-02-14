<template>
  <div
    id="app"
    :class="{ dark: isDark }"
  >
    <RouterView v-if="authStore.isAuthenticated" />
    <div
      v-else
      class="auth-wrapper"
    >
      <RouterView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const isDark = computed(() => themeStore.isDark)

onMounted(() => {
  themeStore.initialize()
})
</script>

<style lang="scss">
#app {
  min-height: 100vh;
}

.auth-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--el-bg-color-page);
}
</style>
