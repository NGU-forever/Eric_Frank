import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  function setTheme(dark: boolean) {
    isDark.value = dark
  }

  function initialize() {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    // Check saved preference
    const saved = localStorage.getItem('theme')

    if (saved === 'dark' || (saved === 'auto' && prefersDark)) {
      isDark.value = true
    }

    // Listen for system changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (localStorage.getItem('theme') === 'auto') {
        isDark.value = e.matches
      }
    })
  }

  // Apply theme to document
  watch(
    isDark,
    (dark) => {
      if (dark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },
    { immediate: true }
  )

  return {
    isDark,
    toggleTheme,
    setTheme,
    initialize,
  }
})
