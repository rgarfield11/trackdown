import { describe, it, expect, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import GameView from '../GameView.vue'
import AudioPlayer from '../../components/AudioPlayer.vue'
import GuessInput from '../../components/GuessInput.vue'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const ANSWER = {
  TRACK_ID: 1,
  TITLE: 'Bohemian Rhapsody',
  ARTIST_NAME: 'Queen',
  ARTIST_ID: 412,
  ALBUM_TITLE: 'A Night at the Opera',
  ALBUM_COVER_URL: 'https://example.com/cover.jpg',
  RELEASE_YEAR: 1975,
  GENRE_NAME: 'Rock',
}

const WRONG_TRACK = {
  TRACK_ID: 2,
  TITLE: 'Smells Like Teen Spirit',
  ARTIST_NAME: 'Nirvana',
  ARTIST_ID: 555,
  ALBUM_TITLE: 'Nevermind',
  ALBUM_COVER_URL: 'https://example.com/cover2.jpg',
  RELEASE_YEAR: 1991,
  GENRE_NAME: 'Grunge',
}

function mockFetchTrack(track = ANSWER) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({ json: () => Promise.resolve(track) }),
  )
}

/**
 * Mount GameView with child components stubbed out and wait for the
 * initial loadTrack() fetch to settle.
 *
 * Components are looked up by their imported definition (not by name string)
 * so that findComponent(GuessInput) / findComponent(AudioPlayer) resolve
 * correctly against the stubs.
 */
async function mountGame() {
  mockFetchTrack()
  const wrapper = mount(GameView, {
    global: {
      stubs: {
        AudioPlayer: true,
        GuessInput: true,
        GuessList: true,
        VinylRecord: true,
      },
    },
  })
  await flushPromises()
  return wrapper
}

/** Emit a 'guess' event from the stubbed GuessInput via its original ref. */
async function emitGuess(wrapper: ReturnType<typeof mount>, track: Record<string, unknown>) {
  wrapper.findComponent(GuessInput).vm.$emit('guess', track)
  await flushPromises()
}

/** Click the Skip button. */
async function clickSkip(wrapper: ReturnType<typeof mount>) {
  await wrapper.find('.btn-skip').trigger('click')
}

/** Click the Give Up button. */
async function clickGiveUp(wrapper: ReturnType<typeof mount>) {
  await wrapper.find('.btn-give-up').trigger('click')
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('GameView', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  // -------------------------------------------------------------------------
  // Initial load
  // -------------------------------------------------------------------------

  it('calls the random-track API on mount', async () => {
    mockFetchTrack()
    const fetchSpy = vi.mocked(fetch)
    mount(GameView, {
      global: { stubs: { AudioPlayer: true, GuessInput: true, GuessList: true, VinylRecord: true } },
    })
    await flushPromises()
    expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining('/tracks/random'))
  })

  it('renders the game UI after the track loads', async () => {
    const wrapper = await mountGame()
    expect(wrapper.find('.game').exists()).toBe(true)
    expect(wrapper.find('.loading').exists()).toBe(false)
  })

  // -------------------------------------------------------------------------
  // Correct guess → won
  // -------------------------------------------------------------------------

  it('sets gameStatus to "won" when the correct track is guessed', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, ANSWER)
    expect(wrapper.find('.result.won').exists()).toBe(true)
  })

  it('does not add a guess entry for a correct answer', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, ANSWER)
    expect(wrapper.findAll('.attempt-dot.used')).toHaveLength(0)
  })

  it('hides GuessInput after winning', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, ANSWER)
    expect(wrapper.findComponent(GuessInput).exists()).toBe(false)
  })

  // -------------------------------------------------------------------------
  // Wrong guess → added to list
  // -------------------------------------------------------------------------

  it('pushes a wrong guess to the list', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, WRONG_TRACK)
    expect(wrapper.findAll('.attempt-dot.used')).toHaveLength(1)
  })

  it('game remains playing after one wrong guess', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, WRONG_TRACK)
    expect(wrapper.find('.result').exists()).toBe(false)
    expect(wrapper.findComponent(GuessInput).exists()).toBe(true)
  })

  // -------------------------------------------------------------------------
  // 6 wrong guesses → lost
  // -------------------------------------------------------------------------

  it('sets gameStatus to "lost" after 6 wrong guesses', async () => {
    const wrapper = await mountGame()
    for (let i = 0; i < 6; i++) {
      await emitGuess(wrapper, WRONG_TRACK)
    }
    expect(wrapper.find('.result.lost').exists()).toBe(true)
  })

  // -------------------------------------------------------------------------
  // Skip
  // -------------------------------------------------------------------------

  it('adds a null guess when skip is clicked', async () => {
    const wrapper = await mountGame()
    await clickSkip(wrapper)
    expect(wrapper.findAll('.attempt-dot.used')).toHaveLength(1)
  })

  it('disables skip button after 5 uses (6th attempt reserved for guessing)', async () => {
    const wrapper = await mountGame()
    for (let i = 0; i < 5; i++) {
      await clickSkip(wrapper)
    }
    expect(wrapper.find('.btn-skip').attributes('disabled')).toBeDefined()
  })

  it('sets gameStatus to "lost" after 5 skips then a wrong guess', async () => {
    const wrapper = await mountGame()
    for (let i = 0; i < 5; i++) {
      await clickSkip(wrapper)
    }
    await emitGuess(wrapper, WRONG_TRACK)
    expect(wrapper.find('.result.lost').exists()).toBe(true)
  })

  // -------------------------------------------------------------------------
  // Give Up
  // -------------------------------------------------------------------------

  it('sets gameStatus to "lost" immediately when Give Up is clicked', async () => {
    const wrapper = await mountGame()
    await clickGiveUp(wrapper)
    expect(wrapper.find('.result.lost').exists()).toBe(true)
  })

  // -------------------------------------------------------------------------
  // currentDuration advances with each guess
  // -------------------------------------------------------------------------

  it('starts with a max-duration of 1 second', async () => {
    const wrapper = await mountGame()
    expect(wrapper.findComponent(AudioPlayer).props('maxDuration')).toBe(1)
  })

  it('increases max-duration by 1 after each wrong guess', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, WRONG_TRACK)
    expect(wrapper.findComponent(AudioPlayer).props('maxDuration')).toBe(2)
  })

  it('caps max-duration at 6 on the final attempt', async () => {
    const wrapper = await mountGame()
    for (let i = 0; i < 5; i++) {
      await emitGuess(wrapper, WRONG_TRACK)
    }
    // 5 wrong guesses → 6th attempt → CLIP_DURATIONS[5] = 6
    expect(wrapper.findComponent(AudioPlayer).props('maxDuration')).toBe(6)
  })

  // -------------------------------------------------------------------------
  // Play Again
  // -------------------------------------------------------------------------

  it('resets the game state after Play Again is clicked', async () => {
    const wrapper = await mountGame()
    await emitGuess(wrapper, WRONG_TRACK)
    await emitGuess(wrapper, WRONG_TRACK)
    await clickGiveUp(wrapper)
    expect(wrapper.find('.result.lost').exists()).toBe(true)

    await wrapper.find('.play-again').trigger('click')
    await flushPromises()

    expect(wrapper.find('.result').exists()).toBe(false)
    expect(wrapper.findAll('.attempt-dot.used')).toHaveLength(0)
  })

  it('fetches a new track after Play Again', async () => {
    const wrapper = await mountGame()
    const fetchSpy = vi.mocked(fetch)
    const callsBefore = fetchSpy.mock.calls.length
    await clickGiveUp(wrapper)
    await wrapper.find('.play-again').trigger('click')
    await flushPromises()
    expect(fetchSpy.mock.calls.length).toBeGreaterThan(callsBefore)
  })
})
