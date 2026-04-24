import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import GuessInput from '../GuessInput.vue'

const SEARCH_RESULTS = [
  {
    TRACK_ID: 1,
    TITLE: 'Bohemian Rhapsody',
    ARTIST_NAME: 'Queen',
    ALBUM_COVER_URL: 'https://example.com/cover.jpg',
    RELEASE_YEAR: 1975,
  },
]

function mockFetch(data: unknown) {
  return vi.fn().mockResolvedValue({ json: () => Promise.resolve(data) })
}

describe('GuessInput', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('renders the search input', () => {
    const wrapper = mount(GuessInput)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('shows no dropdown on initial render', () => {
    const wrapper = mount(GuessInput)
    expect(wrapper.find('.dropdown').exists()).toBe(false)
  })

  it('shows loading state while debounce timer runs', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput)
    await wrapper.find('input').setValue('Queen')
    // Timer hasn't fired yet — should show loading state in dropdown
    expect(wrapper.find('.dropdown').exists()).toBe(true)
    expect(wrapper.find('.dropdown-loading').exists()).toBe(true)
  })

  it('renders search results after debounce fires', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput)
    await wrapper.find('input').setValue('Queen')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    const items = wrapper.findAll('.dropdown li')
    // First item should be a result (not loading/empty)
    expect(items.some((li) => li.text().includes('Bohemian Rhapsody'))).toBe(true)
  })

  it('shows "No results found" when search returns empty', async () => {
    vi.stubGlobal('fetch', mockFetch([]))
    const wrapper = mount(GuessInput)
    await wrapper.find('input').setValue('xyznonexistent')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    expect(wrapper.find('.dropdown-empty').text()).toBe('No results found')
  })

  it('emits guess event with selected track when result is clicked', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput)
    await wrapper.find('input').setValue('Queen')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    const resultItem = wrapper.findAll('.dropdown li').find((li) =>
      li.text().includes('Bohemian Rhapsody'),
    )
    await resultItem!.trigger('mousedown')
    // Assert the full emitted structure to avoid chained index access, which
    // is unsafe under noUncheckedIndexedAccess.
    expect(wrapper.emitted('guess')).toEqual([
      [expect.objectContaining({ TRACK_ID: 1, TITLE: 'Bohemian Rhapsody' })],
    ])
  })

  it('clears the input after a selection', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput)
    await wrapper.find('input').setValue('Queen')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    const resultItem = wrapper.findAll('.dropdown li').find((li) =>
      li.text().includes('Bohemian Rhapsody'),
    )
    await resultItem!.trigger('mousedown')
    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('')
  })

  it('closes dropdown when input is cleared', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput)
    await wrapper.find('input').setValue('Queen')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    await wrapper.find('input').setValue('')
    expect(wrapper.find('.dropdown').exists()).toBe(false)
  })

  it('filters out already-guessed tracks from results', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput, { props: { guessedIds: [1] } })
    await wrapper.find('input').setValue('Queen')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    expect(wrapper.findAll('.dropdown li').some((li) => li.text().includes('Bohemian Rhapsody'))).toBe(false)
  })

  it('shows a track that is not in guessedIds', async () => {
    vi.stubGlobal('fetch', mockFetch(SEARCH_RESULTS))
    const wrapper = mount(GuessInput, { props: { guessedIds: [99] } })
    await wrapper.find('input').setValue('Queen')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    expect(wrapper.findAll('.dropdown li').some((li) => li.text().includes('Bohemian Rhapsody'))).toBe(true)
  })
})
