# Follow-ups — out of scope for this refactor, surfaced along the way

Not bugs introduced by the refactor; pre-existing design gaps worth a later pass.

1. **Google-account profile edit / deletion.** `PUT /auth/profile` and
   `DELETE /auth/account` gate on the account password. Passwordless (Google)
   accounts now get a clear 400 (P4) but still can't self-serve. Proper fix: accept
   a fresh Google ID token as the re-auth for these two endpoints.

2. **Open read endpoints.** `GET /auth/profile?email=`, `GET /orders/{email}`,
   `GET /cart/{email}`, `GET /auth/is-admin?email=` return any user's data given
   their email — no auth at all. Consistent with the "email header = identity"
   demo design, but worth noting.

3. **`agent_model_name = "qwen/qwen3.6-27b"`** — verify this is a real current Groq
   model slug. If wrong, every agent call falls through to the generic error handler.
   As of P7b it is a `settings` field (env: `AGENT_MODEL_NAME`), so it can be changed
   without a code edit once the correct id is known. Default left unchanged pending
   confirmation.

4. **`.gitattributes`** — repo has `core.autocrlf=true` and no `.gitattributes`, so
   every commit logs LF->CRLF warnings. Adding `* text=auto eol=lf` would silence
   them but reformats line endings repo-wide — do it as its own commit, not mid-refactor.
