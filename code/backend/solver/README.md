# solver

Plain Python. This package never imports FastAPI or SQLAlchemy, so it can be read, run and tested
on its own, away from the web application.

What will live here:

- the problem in data classes (cards, slots, rooms, teachers, groups) and a loader for it
- which day, period and room each card is allowed to use
- the CP-SAT model: the hard rules every routine must obey, and the preferences it should try to meet
- an independent validator that checks a finished routine without using the solver
- the checks that run before generating, so bad data is found early
- the explanation: when no routine is possible, find the smallest set of rules that fight each other
  and turn it into plain sentences
- the repair: after a change, move as few lessons as possible
