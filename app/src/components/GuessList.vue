<script setup lang="ts">
defineProps<{
  guesses: Array<{
    track: Record<string, any> | null
    sameArtist: boolean
    sameGenre: boolean
    yearDiff: number
  }>
}>()
</script>

<template>
  <ul class="guesses">
    <li v-for="(g, i) in guesses" :key="i" class="guess" :class="{ skipped: !g.track }">
      <template v-if="g.track">
        <img :src="g.track.ALBUM_COVER_URL" :alt="g.track.ALBUM_TITLE" />
        <div class="info">
          <span class="title">{{ g.track.TITLE }}</span>
          <span class="artist">{{ g.track.ARTIST_NAME }} &middot; {{ g.track.RELEASE_YEAR }}</span>
          <div class="clues">
            <span v-if="g.sameArtist" class="clue correct">Same Artist</span>
            <span v-if="g.sameGenre" class="clue partial">Same Genre</span>
            <span v-if="!g.sameArtist && g.yearDiff <= 5" class="clue partial">
              Within {{ g.yearDiff === 0 ? 'Same Year' : `${g.yearDiff}yr` }}
            </span>
          </div>
        </div>
        <span class="wrong-mark">✕</span>
      </template>
      <template v-else>
        <span class="skip-label">Skipped</span>
      </template>
    </li>
  </ul>
</template>

<style scoped>
.guesses {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.guess {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-surface);
  border-radius: 10px;
  padding: 10px 14px;
  border-left: 3px solid var(--color-wrong);
}

.guess.skipped {
  border-left-color: var(--color-text-muted);
  opacity: 0.6;
}

.guess img {
  width: 44px;
  height: 44px;
  border-radius: 4px;
  object-fit: cover;
  flex-shrink: 0;
}

.info {
  flex: 1;
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
}

.clues {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.clue {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.clue.correct {
  background: rgba(30, 215, 96, 0.15);
  color: var(--color-correct);
}

.clue.partial {
  background: rgba(245, 166, 35, 0.15);
  color: var(--color-partial);
}

.wrong-mark {
  color: var(--color-text-muted);
  font-size: 14px;
  flex-shrink: 0;
}

.skip-label {
  font-size: 13px;
  color: var(--color-text-muted);
  font-style: italic;
}
</style>
