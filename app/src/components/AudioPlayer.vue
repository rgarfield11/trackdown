<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps<{
  trackId: number
  maxDuration: number
}>()

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const previewUrl = () => `${API}/tracks/${props.trackId}/preview`

const isPlaying = ref(false)
const progress = ref(0)
const error = ref<string | null>(null)
const audio = new Audio()

audio.ontimeupdate = () => {
  if (audio.currentTime >= props.maxDuration) {
    audio.pause()
    audio.currentTime = 0
    isPlaying.value = false
    progress.value = 0
    return
  }
  progress.value = (audio.currentTime / props.maxDuration) * 100
}

audio.onended = () => {
  isPlaying.value = false
  progress.value = 0
}

audio.onerror = () => {
  isPlaying.value = false
  error.value = `Audio error: ${audio.error?.message ?? 'unknown'} (code ${audio.error?.code})`
}

watch(() => props.trackId, () => {
  audio.pause()
  audio.src = ''
  audio.currentTime = 0
  isPlaying.value = false
  progress.value = 0
  error.value = null
})

watch(() => props.maxDuration, () => {
  if (isPlaying.value) {
    audio.pause()
    audio.currentTime = 0
    isPlaying.value = false
    progress.value = 0
  }
})

async function toggle() {
  if (isPlaying.value) {
    audio.pause()
    audio.currentTime = 0
    isPlaying.value = false
    progress.value = 0
  } else {
    error.value = null
    audio.src = previewUrl()
    audio.currentTime = 0
    try {
      await audio.play()
      isPlaying.value = true
    } catch (e: any) {
      error.value = e.message
      isPlaying.value = false
    }
  }
}

onBeforeUnmount(() => {
  audio.pause()
  audio.src = ''
})
</script>

<template>
  <div class="player">
    <button class="play-btn" @click="toggle" :aria-label="isPlaying ? 'Pause' : 'Play'">
      <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor">
        <path d="M8 5v14l11-7z" />
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
      </svg>
    </button>

    <div class="progress-track">
      <div class="progress-bar" :style="{ width: progress + '%' }" />
    </div>

    <span class="duration">{{ maxDuration }}s</span>
  </div>
  <p v-if="error" class="audio-error">{{ error }}</p>
</template>

<style scoped>
.player {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-surface);
  border-radius: 50px;
  padding: 10px 20px;
  width: 100%;
}

.play-btn {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-accent);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
  transition: transform 0.1s, opacity 0.1s;
}

.play-btn:active {
  transform: scale(0.93);
}

.play-btn svg {
  width: 22px;
  height: 22px;
}

.progress-track {
  flex: 1;
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--color-accent);
  border-radius: 2px;
  transition: width 0.1s linear;
}

.duration {
  font-size: 13px;
  color: var(--color-text-muted);
  min-width: 24px;
  text-align: right;
}

.audio-error {
  font-size: 12px;
  color: #ff6b6b;
  margin-top: 6px;
  text-align: center;
}
</style>
