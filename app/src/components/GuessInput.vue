<script setup lang="ts">
import { ref, watch } from 'vue'

const emit = defineEmits<{
  guess: [track: Record<string, any>]
}>()

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const query = ref('')
const results = ref<Record<string, any>[]>([])
const open = ref(false)
const loading = ref(false)
let debounceTimer: ReturnType<typeof setTimeout>

watch(query, (val) => {
  clearTimeout(debounceTimer)
  if (!val.trim()) {
    results.value = []
    open.value = false
    loading.value = false
    return
  }
  loading.value = true
  open.value = true
  debounceTimer = setTimeout(async () => {
    const res = await fetch(`${API}/tracks/search?q=${encodeURIComponent(val)}`)
    results.value = await res.json()
    loading.value = false
    open.value = true
  }, 250)
})

function select(track: Record<string, any>) {
  emit('guess', track)
  query.value = ''
  results.value = []
  open.value = false
}
</script>

<template>
  <div class="guess-input">
    <input
      v-model="query"
      type="text"
      placeholder="Search for a song or artist..."
      autocomplete="off"
      @blur="setTimeout(() => { open = false; loading = false }, 150)"
      @focus="open = results.length > 0"
    />

    <ul v-if="open" class="dropdown">
      <li v-if="loading" class="dropdown-loading">
        <span class="spinner" />
        <span>Searching...</span>
      </li>
      <template v-else>
        <li v-for="track in results" :key="track.TRACK_ID" @mousedown="select(track)">
          <img :src="track.ALBUM_COVER_URL" :alt="track.ALBUM_TITLE" />
          <div class="track-info">
            <span class="title">{{ track.TITLE }}</span>
            <span class="artist">{{ track.ARTIST_NAME }} &middot; {{ track.RELEASE_YEAR }}</span>
          </div>
        </li>
        <li v-if="results.length === 0" class="dropdown-empty">No results found</li>
      </template>
    </ul>
  </div>
</template>

<style scoped>
.guess-input {
  position: relative;
  width: 100%;
}

input {
  width: 100%;
  padding: 14px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  color: var(--color-text);
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

input:focus {
  border-color: var(--color-accent);
}

input::placeholder {
  color: var(--color-text-muted);
}

.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  list-style: none;
  overflow: hidden;
  z-index: 10;
  max-height: 320px;
  overflow-y: auto;
}

.dropdown li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown li:active,
.dropdown li:hover {
  background: var(--color-border);
}

.dropdown img {
  width: 44px;
  height: 44px;
  border-radius: 4px;
  object-fit: cover;
  flex-shrink: 0;
}

.track-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.title {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.artist {
  font-size: 12px;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-loading,
.dropdown-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  color: var(--color-text-muted);
  font-size: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
