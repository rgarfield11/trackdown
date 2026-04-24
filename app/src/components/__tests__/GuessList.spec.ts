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
  // Three clue tiles always present
  // -------------------------------------------------------------------------

  it('renders exactly three clue tiles for a non-skipped guess', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess()] } })
    expect(wrapper.findAll('.clue-tile')).toHaveLength(3)
  })

  it('tile labels are Artist, Year, and Genre', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess()] } })
    const labels = wrapper.findAll('.tile-label').map((el) => el.text())
    expect(labels).toEqual(['Artist', 'Year', 'Genre'])
  })

  it('tile values show artist name, release year, and genre', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess()] } })
    const values = wrapper.findAll('.tile-value').map((el) => el.text())
    expect(values).toEqual(['Queen', '1975', 'Rock'])
  })

  // -------------------------------------------------------------------------
  // Artist tile colors
  // -------------------------------------------------------------------------

  it('artist tile has correct class when sameArtist is true', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ sameArtist: true })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[0]!.classes()).toContain('correct')
  })

  it('artist tile has wrong class when sameArtist is false', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ sameArtist: false })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[0]!.classes()).toContain('wrong')
  })

  // -------------------------------------------------------------------------
  // Year tile colors
  // -------------------------------------------------------------------------

  it('year tile has correct class when yearDiff is 0', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ yearDiff: 0 })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[1]!.classes()).toContain('correct')
  })

  it('year tile has close class when yearDiff is between 1 and 5', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ yearDiff: 3 })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[1]!.classes()).toContain('close')
  })

  it('year tile has close class at the boundary of yearDiff === 5', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ yearDiff: 5 })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[1]!.classes()).toContain('close')
  })

  it('year tile has wrong class when yearDiff is greater than 5', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ yearDiff: 6 })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[1]!.classes()).toContain('wrong')
  })

  // -------------------------------------------------------------------------
  // Genre tile colors
  // -------------------------------------------------------------------------

  it('genre tile has correct class when sameGenre is true', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ sameGenre: true })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[2]!.classes()).toContain('correct')
  })

  it('genre tile has wrong class when sameGenre is false', () => {
    const wrapper = mount(GuessList, { props: { guesses: [makeGuess({ sameGenre: false })] } })
    const tiles = wrapper.findAll('.clue-tile')
    expect(tiles[2]!.classes()).toContain('wrong')
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
