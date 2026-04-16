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
const showRules = ref(false)
const guesses = ref<Array<{
  track: Record<string, any> | null
  sameArtist: boolean
  sameGenre: boolean
  yearDiff: number
}>>([])
const gameStatus = ref<'playing' | 'won' | 'lost'>('playing')
const loading = ref(true)

const currentDuration = () => CLIP_DURATIONS[Math.min(guesses.value.length, MAX_GUESSES - 1)] ?? 1

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

    <div class="top-actions">
      <button class="icon-btn" @click="showRules = true" aria-label="How to play" data-tooltip="How to play">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
          <circle cx="12" cy="17" r=".5" fill="currentColor"/>
        </svg>
      </button>
      <a class="icon-btn" href="https://github.com/rgarfield11/trackdown" target="_blank" rel="noopener" aria-label="Github repo" data-tooltip="Github repo">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"/>
        </svg>
      </a>
    </div>

    <!-- Rules modal -->
    <div v-if="showRules" class="modal-backdrop" @click.self="showRules = false">
      <div class="modal">
        <button class="modal-close" @click="showRules = false">✕</button>
        <h2>How to Play</h2>
        <ul>
          <li>Listen to the clip and guess the song.</li>
          <li>You have <strong>6 guesses</strong>. Each wrong guess or skip adds 1 second to the clip.</li>
          <li>Search by song title or artist name to make a guess.</li>
          <li>Wrong guesses show clues — same artist, same genre, or release year within 5 years.</li>
          <li>Hit <strong>Skip</strong> to hear more without guessing.</li>
          <li>Hit <strong>Give Up</strong> to reveal the answer.</li>
        </ul>
      </div>
    </div>

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

  <footer class="attribution">
    <a href="https://www.deezer.com" target="_blank" rel="noopener">Powered by Deezer</a>
  </footer>
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

.top-actions {
  position: fixed;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  z-index: 50;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  transition: color 0.15s, border-color 0.15s;
  text-decoration: none;
  position: relative;
}

.icon-btn:hover {
  color: var(--color-text);
  border-color: var(--color-text-muted);
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

.icon-btn[data-tooltip]:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  font-size: 12px;
  white-space: nowrap;
  padding: 4px 10px;
  border-radius: 6px;
  pointer-events: none;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 24px;
}

.modal {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 28px 24px;
  max-width: 380px;
  width: 100%;
  position: relative;
}

.modal h2 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-accent);
}

.modal ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal li {
  font-size: 14px;
  color: var(--color-text);
  padding-left: 16px;
  position: relative;
  line-height: 1.5;
}

.modal li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-accent);
}

.modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 16px;
  cursor: pointer;
  line-height: 1;
  padding: 4px;
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

.attribution {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 11px;
  color: var(--color-text-muted);
  padding: 16px;
  pointer-events: none;
}

.attribution a {
  color: var(--color-text-muted);
  text-decoration: underline;
  text-underline-offset: 2px;
  pointer-events: all;
}

.attribution a:hover {
  color: var(--color-text);
}
</style>
