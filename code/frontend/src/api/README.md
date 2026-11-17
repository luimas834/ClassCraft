# api

One small client that every request goes through, and one file of hooks per subject. Keeping it in
one place means the sign-in cookie, the error shape and the expired-session case are written once.
