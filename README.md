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
B.Sc. in Software Engineering;
Department of Computer Science and Engineering (CSE)
Islamic University of Technology-IUT, OIC

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

Not available yet. This section is written once the development stack is in place.

Copy `.env.example` to `.env` and change the values marked `change-me` before running anything.

```bash
cp .env.example .env
```

## Licence

MIT. See [LICENSE](LICENSE).
