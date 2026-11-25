import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App.jsx'

// The page asks the backend about its health as soon as it is shown. A test has
// no backend, so we answer that one question ourselves.
function answerHealthWith(body) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({ ok: true, json: async () => body }),
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('shows the name ClassCraft and the API status', async () => {
    answerHealthWith({ status: 'ok', db: 'ok', version: '0.1.0' })

    render(<App />)

    expect(screen.getByRole('heading', { name: 'ClassCraft' })).toBeInTheDocument()
    // findByText waits, because the answer arrives after the first drawing.
    expect(await screen.findByText('API: ok')).toBeInTheDocument()
  })
})
