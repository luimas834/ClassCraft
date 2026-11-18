# ClassCraft

An automated, constraint-based class routine generator for university departments.

ClassCraft builds a department's weekly class routine. The routine committee enters the teachers,
rooms, classes, courses and lessons, and a constraint solver (Google OR-Tools CP-SAT) generates a
routine with no clashes. The committee adjusts the result by dragging cards on a grid and
publishes it. Students need no account: the published routine is a public page that works on a
phone.

Scope: one department, one semester.

## Course

SWE 4506 — Design Project-I
B.Sc. in Software Engineering
Department of Computer Science and Engineering (CSE)
Islamic University of Technology

## Team

| Name | Student ID |
|---|---|
| S.M. Samiul Hossain | 230042110 |
| Maliha Tasnim Khan | 230042127 |
| Arafat Hosen | 230042151 |

Supervisor: Asaduzzaman Herok, Lecturer, CSE.

## Technology

Python 3.12 with OR-Tools CP-SAT for the solver, FastAPI and PostgreSQL 17 for the backend,
React with Vite and Tailwind CSS for the frontend, Docker Compose for running it all.

## How to run

Everything runs in Docker. Nothing is installed on your own machine.

Words used below: an **image** is a packed copy of a program with everything it needs, a
**container** is a running image, and **Docker Compose** starts several containers together from one
file.

### First run, for someone who has never used Docker

1. Install **Docker Desktop** (Windows or macOS) or Docker Engine with the Compose plugin (Linux).
   Start it and wait until it says it is running.
2. Install **Git** and open a terminal.
3. Get the code:

   ```bash
   git clone git@github.com:luimas834/ClassCraft.git
   cd ClassCraft
   ```

4. Copy the settings file. You do not need to edit it for a first try. On Windows PowerShell use
   `copy .env.example .env`.

   ```bash
   cp .env.example .env
   ```

5. Build and start everything. The first time this downloads and builds for a few minutes. Leave the
   terminal open; it shows the logs.

   ```bash
   docker compose up --build
   ```

6. When you see `Application startup complete`, open <http://localhost:5173> in a browser. The page
   shows **ClassCraft** and **API: ok**. The API documentation, which FastAPI writes by itself, is at
   <http://localhost:8000/docs>.
7. To stop: press `Ctrl+C` in the terminal, or run `docker compose down` in another terminal. Your
   data is kept.
8. To start again later: `docker compose up`. You only need `--build` again when the dependencies
   change.

Change the values marked `change-me` in `.env` before anyone outside the team can reach the app.

### Everyday commands

| Command | What it does |
|---|---|
| `make up` | Start the database, backend and frontend in the background |
| `make down` | Stop them. The database keeps its files |
| `make logs` | Follow what all three services are printing |
| `make psql` | Open a database prompt |
| `make shell` | Open a shell inside the backend container |

### If something looks broken

- `docker compose logs backend` shows the backend's messages.
- "port is already allocated" means another program is using 5432, 8000 or 5173. Stop that program,
  or change the number on the left of the `ports:` line in `docker-compose.yml`.
- On Windows, keep the repository inside the WSL 2 file system, otherwise saving a file does not
  reload the page.
- Editing `code/frontend/src/App.jsx` should update the browser without a restart. If it does not,
  the source folder is not mounted; check that you started the stack from the repository folder.

## Licence

MIT. See [LICENSE](LICENSE).
