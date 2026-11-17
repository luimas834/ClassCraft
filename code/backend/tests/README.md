# tests

The backend tests, run with pytest. They are split by what they test, so one part can be run alone
while working on it.

| Folder | What it tests |
|---|---|
| `solver/` | The rules, the validator, the explanation and the repair, without a database |
| `api/` | The endpoints, one file per router: who may call them and what they answer |
| `services/` | Importing, exporting, and building the views the grid uses |
| `e2e/` | One whole flow over real HTTP, from entering data to a published routine |
| `fixtures/` | Small invented departments used by the tests: a tiny one, an impossible one, a medium one |

Tests use invented names, never real people.
