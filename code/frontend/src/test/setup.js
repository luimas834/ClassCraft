// Runs once before the frontend tests.
// It adds the extra checks of jest-dom, such as toBeInTheDocument, and empties
// the pretend page after every test so one test cannot affect the next one.

import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
