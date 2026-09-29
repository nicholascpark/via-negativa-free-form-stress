# Agent Mode Examples

## Worked Example: Pre-Execution Audit

### The Scenario

A coding agent is tasked with fixing a bug: "Users report that search
results are slow when filtering by date range." The agent has analyzed
the code, identified that the `search_orders` query lacks an index on
`created_at`, and plans to add the index.

### The Agent's Plan

> I've identified the root cause: the `orders` table has no index on
> `created_at`. The query does a full table scan when filtering by date
> range. I'll add a migration to create the index:
> `CREATE INDEX idx_orders_created_at ON orders(created_at);`

### Pre-Execution Audit

**Proceed**: yes-with-caveats

**Blind spots**:
- The query filters on `created_at` but also joins `order_items` and
  filters on `status`. A single-column index on `created_at` may not
  eliminate the slowness — the query planner may still scan for the
  join/filter combination. Check the full query plan, not just the
  WHERE clause.
- Adding an index to a production table with 50M+ rows will lock the
  table during creation unless done concurrently. The plan doesn't
  address migration safety.

**Fragile assumptions**:
- "The slow query is the search_orders query" — the agent traced from
  the symptom (slow search) to a query, but didn't verify this is the
  actual slow query in production. There may be multiple queries behind
  the search endpoint. Validate with query logs or APM data before
  committing to the fix.

**Frame check**: mismatch
- The agent is solving "missing index" when the problem presented is
  "slow search results with date filter." These aren't the same problem.
  Missing index is one possible cause. Others: N+1 queries in the
  search path, missing query cache, the date filter generating an
  unbounded range that returns too many rows regardless of index. The
  agent jumped from symptom to solution without confirming the diagnosis.

**Recommendation**: Pause. Verify the diagnosis by checking the actual
query plan and confirming that the index addresses the dominant cost.
Then proceed with `CREATE INDEX CONCURRENTLY` for migration safety.

---

## Worked Example: Loop-Break Diagnostic

### The Scenario

A coding agent is trying to fix a failing test. The test asserts that
after a user is deleted, their associated records in three other tables
are also deleted (cascade). The agent has:

1. **Attempt 1**: Added `ON DELETE CASCADE` to the foreign key on
   `user_preferences`. Test still fails.
2. **Attempt 2**: Added `ON DELETE CASCADE` to the foreign key on
   `user_sessions`. Test still fails.
3. **Attempt 3**: Checked the foreign key on `user_audit_log` — it
   already has CASCADE. Reran the test. Still fails.

The agent is about to check if there's a fourth table it missed.

### Loop-Break Diagnostic

**Loop pattern**: The agent is iterating through tables adding CASCADE
constraints, one at a time, rerunning the test after each. Each attempt
fixes one table but the test still fails.

**Why it's stuck**: False unity. The agent is treating this as one
problem ("missing CASCADE") when there are likely two problems:
1. Missing CASCADE constraints (which the agent is fixing incrementally)
2. Something else entirely that also causes the test to fail

The agent's loop structure (fix one thing → rerun → fail → fix another
thing) means it never gets clean signal on whether the CASCADE fixes
are working, because the test has a second failure mode masking the
first.

**The agent's current frame**: "The test fails because CASCADE is missing
on some foreign keys. I need to find which ones."

**What the frame excludes**: The possibility that CASCADE is only part
of the problem. The test might also be failing because: the deletion
is wrapped in a transaction that gets rolled back before the assertions
run; the test's database connection is different from the app's connection
(common in test setups with connection pooling); or the assertion checks
a cache, not the database.

**Escape vector**: Run all CASCADE fixes simultaneously (not one at a
time), then rerun. If the test still fails, the problem is not CASCADE.
Read the test's actual assertion and trace what it's checking — is it
querying the database directly, or checking through an application
layer that might have stale state?

**What to stop doing**: Stop the one-fix-at-a-time-rerun cycle. It
produces ambiguous signal because you can't distinguish "my fix didn't
work" from "my fix worked but something else is also broken."

---

## Worked Example: Task-Framing Challenge

### The Scenario

A user asks their coding agent: "Refactor the notification service to
use a message queue instead of direct HTTP calls. We need to decouple
it from the other services."

### Task-Framing Challenge

**Inherited assumptions in this request**:
- "A message queue is the right decoupling mechanism" — message queues
  decouple in time (async) and deployment, but they also introduce
  complexity: delivery guarantees, ordering, dead letter handling,
  operational overhead. If the pain point is deployment coupling (can't
  deploy service A without service B), a message queue solves that. If
  the pain point is code coupling (notification logic is tangled with
  business logic), a message queue won't help — the coupling moves from
  HTTP client code to message publishing code. Worth confirming which
  kind of coupling is the actual pain.
- "The notification service is the right boundary" — the request takes
  the current service boundary as given. If the notification service
  does email, SMS, push, and in-app notifications with different
  reliability requirements, a single queue might not be the right
  abstraction. The refactoring scope might need to change with the
  decoupling mechanism.

**The problem behind the request**:
The user wants to reduce the blast radius of notification failures —
when the notification service is slow or down, it shouldn't affect the
services that trigger notifications. A message queue achieves this, but
so does a simple async HTTP call with a retry queue, which is less
infrastructure change.

**What you'll encounter that you haven't planned for**:
- The current HTTP calls likely carry request context (user ID, session
  info, correlation IDs) that will need to be serialized into messages.
  The message schema becomes a contract that's harder to change than an
  HTTP endpoint — design the schema before writing code, because
  changing it after other services publish to the queue requires
  coordinated migration.
- Error visibility will change fundamentally. Today, a failed
  notification returns an HTTP error to the caller, who can decide what
  to do. With a queue, failures become invisible to the caller and
  visible only through dead letter queue monitoring — which doesn't
  exist yet. You'll need to build that observability before or during
  the migration, not after.

---

## Worked Example: Loop-Break in Debugging

### The Scenario

A coding agent is debugging a race condition in a web application.
Users intermittently see stale data after updating their profile.
The agent has:

1. **Attempt 1**: Added cache invalidation after the profile update.
   Bug still occurs.
2. **Attempt 2**: Changed cache invalidation to happen before the
   database write returns. Bug still occurs.
3. **Attempt 3**: Added a 500ms delay after invalidation before
   redirecting. Bug frequency reduced but not eliminated.

### Loop-Break Diagnostic

**Loop pattern**: The agent is iterating on cache invalidation timing.
Each attempt adjusts *when* the cache is invalidated relative to the
write. The partial success of Attempt 3 (delay reduces frequency)
has reinforced the agent's belief that this is a timing problem.

**Why it's stuck**: Frame lock. The agent is locked into "this is a
cache invalidation timing problem" because Attempt 3 produced partial
improvement. But partial improvement from adding a delay is consistent
with multiple different root causes — it's weak evidence that has
anchored the agent to the wrong frame.

**The agent's current frame**: "The cache serves stale data because
invalidation doesn't happen fast enough."

**What the frame excludes**: The possibility that there are *multiple
caches*. If the application has both a server-side cache and a CDN
or browser cache, invalidating the server cache doesn't touch the
other layers. The delay in Attempt 3 "worked" because it gave the
CDN's TTL time to expire — not because it fixed the invalidation
timing. Another exclusion: the read and write might hit different
database replicas with replication lag. The "stale data" might not
be a cache problem at all.

**Escape vector**: Stop tuning cache invalidation timing. Instead,
map all the layers between "data written" and "user sees updated
data." Enumerate every place a stale value could be served: application
cache, CDN, browser cache, database read replica. Then determine
which layer is actually serving the stale read. The agent has been
fixing Layer 2 while the problem may be in Layer 4.

**What to stop doing**: Stop using "did the frequency change" as the
success metric. A delay-based improvement is ambiguous — it tells you
the problem is time-sensitive, not that you've found the right layer.
Get deterministic signal: log the exact response headers and data
source on a stale read.
