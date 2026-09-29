# Code & PR Review Examples

## Worked Example: Authentication Middleware PR (Embedded Artifact Analysis)

### The Artifact
A PR adds JWT-based auth middleware to an Express app. It validates tokens,
extracts user info, and attaches it to the request object. Tests pass.
Standard review says: "Looks good, approve."

### Step 0.5: Context Acquisition
Before analyzing the PR itself, examine what it's embedded in:
- The codebase has no existing auth — this is the first auth surface.
- There are two other open PRs: one adding a user profile endpoint,
  one adding an admin dashboard. Both assume auth exists but neither
  coordinates with this PR on token shape or permission model.
- The commit history shows the author initially tried Passport.js,
  abandoned it (3 reverted commits), and switched to raw JWT. The PR
  description doesn't explain why.
- The roadmap includes "multi-tenant support" in Q3. The JWT payload
  structure has no tenant field.

### Layer 1: Absence Inventory (with context)

| Missing | Risk | Severity |
|---------|------|----------|
| No coordination with the two other auth-dependent PRs on token payload shape | Profile and admin PRs will ship assuming different token structures, causing integration failures at merge | Critical |
| No explanation of why Passport.js was abandoned | Next engineer assigned auth work will evaluate Passport.js again, waste the same time, hit the same wall | Significant |
| No tenant identifier in token payload | Q3 multi-tenant feature will require a breaking token schema migration that invalidates all active sessions | Significant |
| No rate limiting on auth endpoint | Brute force attacks possible | Significant |
| No audit logging of auth failures | Can't detect attack patterns post-deploy | Minor |

Note: "missing token refresh" and "missing clock skew handling" were
candidate findings but are intentional — the PR description explicitly
scopes this as "v1 auth, refresh in follow-up."

### Layer 2: Load-Bearing Assumptions

**"This PR is the only thing introducing auth"** (Invisible)
- The two other open PRs are building their own auth assumptions independently.
  This PR doesn't just add auth — it silently becomes the auth contract for
  the whole system, but nobody has agreed to that contract.
- Fragility: High. The token payload is now a de facto API, but it's
  not documented or versioned as one.
- Hedge: Publish the token schema as an internal contract before merging.
  Get sign-off from the profile and admin PR authors.

**"Auth can be added incrementally"** (Plausible but fragile)
- The middleware intercepts all routes. But auth is a cross-cutting concern
  that changes error handling, logging, and API contracts everywhere.
  The PR treats it as additive; the system experiences it as transformative.
- Hedge: Audit existing error handlers and API responses for auth-unaware
  assumptions (e.g., endpoints that return 200 when they should now return 401).

### Layer 3: Frame Exclusions

**Synthesis (2→3)**: Layers 1–2 surfaced: no coordination on token shape,
no explanation of abandoned approach, no tenant field, an invisible assumption
that "this PR is the only thing introducing auth," and the assumption that
"auth can be added incrementally." Ask: what single frame makes all of these
invisible at once? The answer: the frame that treats auth as *middleware* —
a local, per-request concern. Inside that frame, system-level coordination,
contract documentation, and lifecycle planning are literally out of scope.
That's the frame to analyze.

**Frame**: "Auth is middleware" — a request-level interception pattern.

**Illuminates**: Clean separation of concerns, easy to add/remove from routes,
familiar Express pattern.

**Structurally excludes**:
- Auth as a system-level property (service mesh, API gateway, zero-trust)
- Auth as a relationship (who can access what, not just "is this token valid")
- Auth as a lifecycle (provisioning, rotation, revocation, audit trail)

The middleware frame reduces auth to a per-request boolean: valid or not.
This is fine for v1 but the frame will actively resist the permission model,
multi-tenancy, and session management the roadmap requires.

**Recommendation**: Don't reframe now, but add an ADR (Architecture Decision Record)
documenting that middleware-auth was chosen for v1 speed and will need to
evolve into a gateway or service-level pattern before multi-tenant ships.

### Layer 4: Via Negativa Design

**Synthesis (3→4)**: Layer 3 showed the middleware frame structurally excludes
auth as system-level property, relationship, and lifecycle. Ask: given what
the frame excludes, what is this PR *trying to become* that the frame won't
let it? It's trying to be the system's auth contract — but the middleware
frame keeps it scoped as "my middleware." The latent design is the contract
itself.

**Pattern**: Every significant absence clusters around the same theme —
this PR introduces auth as a *feature* when the system needs auth as a
*contract*. The token payload, the error model, the permission boundaries
are all undocumented because the PR frames auth as "my middleware" not
"our system's auth layer."

**Minimum viable intervention**: Before merging, write a one-page
"Auth Contract" doc: token schema (versioned), error codes, what the
middleware guarantees and what it doesn't. Share with the other PR authors.
This costs 30 minutes and prevents weeks of integration pain.

**Resist adding**: Don't add multi-tenant support, refresh tokens, or
a permission model to this PR. The contract doc is what's needed, not
more code.

---

## Worked Example: Database Migration PR

### The Artifact
A PR adds a new `preferences` JSONB column to the `users` table with a
default of `{}`. Migration runs forward only.

### Layer 1: Absence Inventory (Top 3)

1. **No rollback migration** — If deploy fails midway, no path back. (Critical)
2. **No backfill strategy** — Existing rows get `{}` but app code may expect populated fields. (Significant)
3. **No index on JSONB paths** — If preferences are queried, performance degrades silently. (Significant)

### Layer 2: Key Load-Bearing Assumption

**"The JSONB column won't grow unboundedly"**
No size constraint, no schema validation. Users could store unlimited nested data.
If any code path lets users write arbitrary keys, storage and query costs grow without bound.

### Layer 3: Frame Exclusion

**Frame**: Schema-on-write relational model + schemaless JSONB escape hatch.

**Excludes**: The JSONB column is a way to avoid schema design. It defers the question
"what are preferences, exactly?" If this column succeeds, it'll eventually need
internal schema validation (JSON Schema, or migration to typed columns) — but the
JSONB frame makes that feel optional when it's actually inevitable.

---

## Quick Diagnostic Questions for Any PR

When you don't have time for full analysis, ask these five questions:

1. **What error does a user see if this fails?** (If unknown → absence)
2. **What happens when this runs on data that doesn't exist yet?** (Future state assumption)
3. **Can this be undone?** (Rollback absence)
4. **What's the first thing that breaks at 10x scale?** (Load-bearing assumption)
5. **Why was this approach chosen over alternatives?** (Frame awareness)

---

## Worked Example: PR Analyzed as Embedded Artifact (Step 0.5 applied)

### The Artifact
A PR adds a rate limiting middleware to an API gateway. The diff is clean,
tests pass, the implementation uses a token bucket algorithm with Redis
as the backing store. Standard review says: "Clean code, good tests, approve."

### Step 0.5: Context Acquired
Reading the broader codebase reveals:
- Two other open PRs also touch the API gateway (auth refactor, logging overhaul)
- The system is mid-migration from monolith to microservices
- There's a TODO in the deploy config: "move to distributed rate limiting when
  we go multi-region" with no ticket attached
- The Redis instance is shared with session storage and a job queue

### Layer 1 (system-aware, not just PR-aware)

| Missing | Risk | Severity |
|---------|------|----------|
| No coordination with the auth refactor PR | Both touch request middleware; merge order matters and nobody's flagged it | Critical |
| Rate limit config not externalized | When the multi-region migration happens, every region gets the same limits — or someone forks the config and they drift | Significant |
| No load test against shared Redis | Rate limiting adds write pressure to a Redis instance already serving sessions and jobs; under load this could degrade auth | Significant |

Note: The first finding is invisible from inside the PR. The third finding
is invisible without knowing the infrastructure context. These are the
findings that standard code review misses.

### Layer 2: Newly Fragile Inherited Assumption

**"Redis has capacity headroom"**
- This was a reasonable assumption before this PR. Session storage and job
  queues have predictable load patterns. But rate limiting writes on every
  single request. This PR didn't choose Redis — it inherited it — but it
  dramatically changed the load profile on an inherited dependency.
- Fragility: Was robust, now fragile.
- Hedge: Benchmark Redis under combined load, or isolate rate limiting
  to its own Redis instance.

### Layer 3: Frame Mismatch

The PR frames rate limiting as a **gateway-level concern** — middleware that
sits at the edge. But the system is migrating to microservices, where each
service will eventually have its own entry points. Gateway-level rate limiting
is the monolith's framing; the microservices framing would be distributed
rate limiting at the service mesh layer.

This isn't wrong today. But the PR is building infrastructure that only
makes sense in the architecture the team is actively leaving. The
multi-region TODO in the deploy config confirms someone already knows
this, but the knowledge hasn't reached this PR.

**Recommendation**: Ship the PR (it solves the immediate need), but add
an ADR documenting that this is transitional infrastructure with a planned
replacement path, so the next person doesn't invest in hardening something
that's meant to be temporary.
