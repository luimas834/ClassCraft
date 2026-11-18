# src

The React application. Plain JavaScript, styled with Tailwind CSS.

| Folder | What goes in it |
|---|---|
| `api/` | Every call to the server, one file per subject. No component calls the server by itself |
| `auth/` | Who is signed in, and keeping pages away from people who may not see them |
| `components/` | Pieces used on more than one screen: the shared parts, the page frame, the routine grid |
| `features/` | One folder per screen, named after the screen, with its own tests next to it |
| `stores/` | The routine editor's state, which is too busy to keep in the components |
| `lib/` | Small helpers: colours, formatting dates and times, keyboard shortcuts |
| `styles/` | Tailwind and the design tokens: the colours, spacing and type sizes every screen uses |
