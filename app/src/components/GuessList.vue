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
          <div class="clue-tiles">
            <div class="clue-tile" :class="g.sameArtist ? 'correct' : 'wrong'">
              <span class="tile-label">Artist</span>
              <span class="tile-value">{{ g.track.ARTIST_NAME }}</span>
            </div>
            <div
              class="clue-tile"
              :class="g.yearDiff === 0 ? 'correct' : g.yearDiff <= 5 ? 'close' : 'wrong'"
            >
              <span class="tile-label">Year</span>
              <span class="tile-value">{{ g.track.RELEASE_YEAR }}</span>
            </div>
            <div class="clue-tile" :class="g.sameGenre ? 'correct' : 'wrong'">
              <span class="tile-label">Genre</span>
              <span class="tile-value">{{ g.track.GENRE_NAME }}</span>
            </div>
          </div>
        </div>
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

.clue-tiles {
  display: flex;
  gap: 5px;
  margin-top: 6px;
}

.clue-tile {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3px 6px;
  border-radius: 6px;
  min-width: 0;
  overflow: hidden;
}

.tile-label {
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.75;
}

.tile-value {
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  text-align: center;
}

.clue-tile.correct {
  background: rgba(76, 175, 100, 0.2);
  color: #4caf64;
}

.clue-tile.close {
  background: rgba(210, 180, 30, 0.2);
  color: #d4b84a;
}

.clue-tile.wrong {
  background: rgba(200, 80, 60, 0.15);
  color: #c85040;
}


.skip-label {
  font-size: 13px;
  color: var(--color-text-muted);
  font-style: italic;
}
</style>
