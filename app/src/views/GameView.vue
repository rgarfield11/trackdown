<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AudioPlayer from '../components/AudioPlayer.vue'
import GuessInput from '../components/GuessInput.vue'
import GuessList from '../components/GuessList.vue'
import VinylRecord from '../components/VinylRecord.vue'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const CLIP_DURATIONS = [1, 2, 3, 4, 5, 6]
const MAX_GUESSES = CLIP_DURATIONS.length

const track = ref<Record<string, any> | null>(null)
const isPlaying = ref(false)
const guesses = ref<Array<{
  track: Record<string, any>
  sameArtist: boolean
  sameGenre: boolean
  yearDiff: number
}>>([])
const gameStatus = ref<'playing' | 'won' | 'lost'>('playing')
const loading = ref(true)

const currentDuration = () => CLIP_DURATIONS[Math.min(guesses.value.length, MAX_GUESSES - 1)]

async function loadTrack() {
  loading.value = true
  const res = await fetch(`${API}/tracks/random`)
  track.value = await res.json()
  loading.value = false
}

function onGuess(guessed: Record<string, any>) {
  if (!track.value || gameStatus.value !== 'playing') return

  const answer = track.value
  const isCorrect = guessed.TRACK_ID === answer.TRACK_ID

  if (isCorrect) {
    gameStatus.value = 'won'
    return
  }

  guesses.value.push({
    track: guessed,
    sameArtist: guessed.ARTIST_ID === answer.ARTIST_ID,
    sameGenre: guessed.GENRE_NAME === answer.GENRE_NAME,
    yearDiff: Math.abs((guessed.RELEASE_YEAR ?? 0) - (answer.RELEASE_YEAR ?? 0)),
  })

  if (guesses.value.length >= MAX_GUESSES) {
    gameStatus.value = 'lost'
  }
}

function skip() {
  if (!track.value || gameStatus.value !== 'playing') return

  guesses.value.push({ track: null, sameArtist: false, sameGenre: false, yearDiff: Infinity })

  if (guesses.value.length >= MAX_GUESSES) {
    gameStatus.value = 'lost'
  }
}

function giveUp() {
  if (gameStatus.value !== 'playing') return
  gameStatus.value = 'lost'
}

function playAgain() {
  guesses.value = []
  gameStatus.value = 'playing'
  loadTrack()
}

onMounted(loadTrack)
</script>

<template>
  <div class="game">
    <header class="header">
      <h1>TrackDown</h1>
      <p class="subtitle">Guess the song from the clip</p>
    </header>

    <VinylRecord :spinning="isPlaying" />

    <div v-if="loading" class="loading">
      <span class="spinner" />
      Loading track...
    </div>

    <template v-else-if="track">
      <AudioPlayer
        :track-id="track.TRACK_ID"
        :max-duration="currentDuration()"
        :loop="gameStatus !== 'playing'"
        @playing="isPlaying = $event"
      />

      <div class="attempts">
        <span
          v-for="(_, i) in CLIP_DURATIONS"
          :key="i"
          class="attempt-dot"
          :class="{
            used: i < guesses.length,
            current: i === guesses.length && gameStatus === 'playing',
          }"
        />
      </div>

      <GuessList v-if="guesses.length" :guesses="guesses" />

      <div v-if="gameStatus === 'playing'" class="actions">
        <button class="btn-skip" @click="skip" :disabled="guesses.length >= MAX_GUESSES - 1" title="Use a turn to hear more">
          Skip (+1s)
        </button>
        <button class="btn-give-up" @click="giveUp">Give Up</button>
      </div>

      <GuessInput v-if="gameStatus === 'playing'" @guess="onGuess" />

      <div v-if="gameStatus === 'won'" class="result won">
        <img :src="track.ALBUM_COVER_URL" :alt="track.ALBUM_TITLE" class="result-cover" />
        <div class="result-info">
          <p class="result-label">You got it in {{ guesses.length + 1 }}!</p>
          <p class="result-title">{{ track.TITLE }}</p>
          <p class="result-artist">{{ track.ARTIST_NAME }} &middot; {{ track.RELEASE_YEAR }}</p>
        </div>
        <button class="play-again" @click="playAgain">Play Again</button>
      </div>

      <div v-if="gameStatus === 'lost'" class="result lost">
        <img :src="track.ALBUM_COVER_URL" :alt="track.ALBUM_TITLE" class="result-cover" />
        <div class="result-info">
          <p class="result-label">The answer was</p>
          <p class="result-title">{{ track.TITLE }}</p>
          <p class="result-artist">{{ track.ARTIST_NAME }} &middot; {{ track.RELEASE_YEAR }}</p>
        </div>
        <button class="play-again" @click="playAgain">Play Again</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.game {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header {
  text-align: center;
  padding: 8px 0;
}

.header h1 {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--color-accent);
}

.subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--color-text-muted);
  padding: 40px 0;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.attempts {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.attempt-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-border);
  transition: background 0.2s;
}

.attempt-dot.used {
  background: var(--color-wrong);
}

.attempt-dot.current {
  background: var(--color-accent);
}

.result {
  background: var(--color-surface);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
  border-top: 3px solid var(--color-wrong);
}

.result.won {
  border-top-color: var(--color-correct);
}

.result-cover {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  object-fit: cover;
}

.result-label {
  font-size: 13px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.result-title {
  font-size: 20px;
  font-weight: 700;
  margin-top: 4px;
}

.result-artist {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.play-again {
  margin-top: 4px;
  padding: 12px 32px;
  background: var(--color-accent);
  color: #1a1410;
  border: none;
  border-radius: 50px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s;
}

.play-again:active {
  opacity: 0.8;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn-skip,
.btn-give-up {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-skip {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-skip:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-give-up {
  background: rgba(200, 80, 60, 0.1);
  color: #c85040;
  border: 1px solid rgba(200, 80, 60, 0.25);
}

.btn-skip:not(:disabled):active,
.btn-give-up:active {
  opacity: 0.7;
}
</style>
