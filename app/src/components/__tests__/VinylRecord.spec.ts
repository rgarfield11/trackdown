import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VinylRecord from '../VinylRecord.vue'

describe('VinylRecord', () => {
  it('renders the vinyl image', () => {
    const wrapper = mount(VinylRecord, { props: { spinning: false } })
    expect(wrapper.find('img.vinyl').exists()).toBe(true)
  })

  it('does not apply spinning class when spinning is false', () => {
    const wrapper = mount(VinylRecord, { props: { spinning: false } })
    expect(wrapper.find('img.vinyl').classes()).not.toContain('spinning')
  })

  it('applies spinning class when spinning is true', () => {
    const wrapper = mount(VinylRecord, { props: { spinning: true } })
    expect(wrapper.find('img.vinyl').classes()).toContain('spinning')
  })

  it('reactively adds spinning class when prop changes to true', async () => {
    const wrapper = mount(VinylRecord, { props: { spinning: false } })
    expect(wrapper.find('img.vinyl').classes()).not.toContain('spinning')
    await wrapper.setProps({ spinning: true })
    expect(wrapper.find('img.vinyl').classes()).toContain('spinning')
  })
})
