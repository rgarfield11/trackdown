import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GuessList from '../GuessList.vue'

const TRACK = {
  TRACK_ID: 1,
  TITLE: 'Bohemian Rhapsody',
  ARTIST_NAME: 'Queen',
  ARTIST_ID: 412,
  ALBUM_TITLE: 'A Night at the Opera',
  ALBUM_COVER_URL: 'https://example.com/cover.jpg',
  RELEASE_YEAR: 1975,
  GENRE_NAME: 'Rock',
}

function makeGuess(overrides = {}) {
  return { track: TRACK, sameArtist: false, sameGenre: false, yearDiff: 10, ...overrides }
}

describe('GuessList', () => {
  // -------------------------------------------------------------------------
  // Skipped turn
  // -------------------------------------------------------------------------

  it('renders "Skipped" label for a null-track guess', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [{ track: null, sameArtist: false, sameGenre: false, yearDiff: Infinity }] },
    })
    expect(wrapper.find('.skip-label').text()).toBe('Skipped')
  })

  it('applies the skipped CSS class for a null-track guess', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [{ track: null, sameArtist: false, sameGenre: false, yearDiff: Infinity }] },
    })
    expect(wrapper.find('li.guess').classes()).toContain('skipped')
  })

  // -------------------------------------------------------------------------
  // Track info rendering
  // -------------------------------------------------------------------------

  it('renders title and artist for a non-skipped guess', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess()] } })
    expect(wrapper.find('.title').text()).toBe('Bohemian Rhapsody')
    expect(wrapper.find('.artist').text()).toContain('Queen')
    expect(wrapper.find('.artist').text()).toContain('1975')
  })

  it('renders album cover image', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess()] } })
    const img = wrapper.find('img')
    expect(img.attributes('src')).toBe('https://example.com/cover.jpg')
  })

  // -------------------------------------------------------------------------
  // Clue badges
  // -------------------------------------------------------------------------

  it('shows Same Artist clue when sameArtist is true', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ sameArtist: true })] } })
    const clues = wrapper.findAll('.clue')
    expect(clues.some((c) => c.text() === 'Same Artist')).toBe(true)
  })

  it('shows Same Genre clue when sameGenre is true', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ sameGenre: true })] } })
    const clues = wrapper.findAll('.clue')
    expect(clues.some((c) => c.text() === 'Same Genre')).toBe(true)
  })

  it('shows Within Xyr clue when yearDiff <= 5 and sameArtist is false', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [makeGuess({ sameArtist: false, yearDiff: 3 })] },
    })
    const clues = wrapper.findAll('.clue')
    expect(clues.some((c) => c.text().includes('Within'))).toBe(true)
    expect(clues.some((c) => c.text().includes('3yr'))).toBe(true)
  })

  it('shows "Same Year" when yearDiff is 0 and sameArtist is false', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [makeGuess({ sameArtist: false, yearDiff: 0 })] },
    })
    expect(wrapper.text()).toContain('Same Year')
  })

  it('does not show year clue when yearDiff > 5', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [makeGuess({ sameArtist: false, yearDiff: 6 })] },
    })
    const clues = wrapper.findAll('.clue')
    expect(clues.some((c) => c.text().includes('Within'))).toBe(false)
  })

  it('suppresses year clue when sameArtist is true even if yearDiff <= 5', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [makeGuess({ sameArtist: true, yearDiff: 1 })] },
    })
    const clues = wrapper.findAll('.clue')
    expect(clues.some((c) => c.text().includes('Within'))).toBe(false)
  })

  it('shows no clues when nothing matches', () => {
    const wrapper = mount(GuessList, {
      props: { guesses: [makeGuess({ sameArtist: false, sameGenre: false, yearDiff: 20 })] },
    })
    expect(wrapper.findAll('.clue')).toHaveLength(0)
  })

  // -------------------------------------------------------------------------
  // Multiple guesses
  // -------------------------------------------------------------------------

  it('renders one list item per guess', () => {
    const guesses = [makeGuess(), makeGuess({ sameArtist: true }), { track: null, sameArtist: false, sameGenre: false, yearDiff: Infinity }]
    const wrapper = mount(GuessList, { props: { guesses } })
    expect(wrapper.findAll('li.guess')).toHaveLength(3)
  })
})
