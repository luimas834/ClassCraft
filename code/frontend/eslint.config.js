// What ESLint reads and complains about in the frontend.
// ESLint 9 uses "flat" configuration: one array, where each entry adds settings
// for a group of files. The last entry that matches a file wins.

import js from '@eslint/js'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import globals from 'globals'

export default [
  // Folders with code we did not write or that is generated.
  { ignores: ['dist', 'node_modules', 'coverage'] },

  // The rules that catch real mistakes: unused variables, undefined names.
  js.configs.recommended,

  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      // Our code runs in the browser, so window, document and fetch exist.
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      // Without the version the React plugin prints a warning on every run.
      react: { version: '18.3' },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...react.configs.flat.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // Vite uses the new JSX transform, so a file with JSX need not import React.
      'react/react-in-jsx-scope': 'off',
      // The stack has no prop-types library, so this rule can never be satisfied.
      'react/prop-types': 'off',
    },
  },

  // The configuration files at the top of the folder run in Node, not in a browser.
  {
    files: ['*.config.js'],
    languageOptions: { globals: globals.node },
  },
]
