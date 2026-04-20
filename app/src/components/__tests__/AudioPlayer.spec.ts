import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AudioPlayer from '../AudioPlayer.vue'

function makeMockAudio() {
  return {
    play: vi.fn().mockResolvedValue(undefined),
    pause: vi.fn(),
    loop: false,
    src: '',
    currentTime: 0,
    duration: 30,
    ontimeupdate: null as (() => void) | null,
    onended: null as (() => void) | null,
    onerror: null as (() => void) | null,
    error: null,
  }
}

describe('AudioPlayer', () => {
  let mockAudio: ReturnType<typeof makeMockAudio>

  beforeEach(() => {
    mockAudio = makeMockAudio()
    vi.stubGlobal('Audio', function () { return mockAudio })
  })

  it('sets audio.loop = true when loop prop becomes true', async () => {
    const wrapper = mount(AudioPlayer, { props: { trackId: 1, maxDuration: 5, loop: false } })
    expect(mockAudio.loop).toBe(false)
    await wrapper.setProps({ loop: true })
    await flushPromises()
    expect(mockAudio.loop).toBe(true)
  })

  it('sets audio.loop = false when loop prop becomes false', async () => {
    const wrapper = mount(AudioPlayer, { props: { trackId: 1, maxDuration: 5, loop: true } })
    await flushPromises()
    await wrapper.setProps({ loop: false })
    expect(mockAudio.loop).toBe(false)
  })

  it('calls play() when loop prop becomes true', async () => {
    const wrapper = mount(AudioPlayer, { props: { trackId: 1, maxDuration: 5, loop: false } })
    await wrapper.setProps({ loop: true })
    await flushPromises()
    expect(mockAudio.play).toHaveBeenCalled()
  })

  it('does not manually replay in onended when looping', async () => {
    mount(AudioPlayer, { props: { trackId: 1, maxDuration: 5, loop: true } })
    await flushPromises()
    mockAudio.play.mockClear()
    mockAudio.onended?.()
    expect(mockAudio.play).not.toHaveBeenCalled()
  })
})
