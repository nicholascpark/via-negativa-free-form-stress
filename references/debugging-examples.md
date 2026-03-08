# Debugging Examples (Diagnostic Mode)

## Worked Example: Intermittent Test Failure

### The Symptom
`test_payment_processing` fails ~5% of the time in CI. Passes locally.
The team has added retries to the CI config. The test has been marked
"flaky" for three months.

### Step D: Diagnostic Intake

**Assumption chain** (what must be true for this test to pass):
1. Test publishes a payment event to the message queue
2. Payment service processes the event
3. Payment record appears in the database
4. Test asserts the record exists

**Where the chain breaks**: Between steps 2 and 4. The test asserts
immediately after publishing. It assumes processing is fast enough that
by the time the assertion runs, the side effect is complete.

### Layer 1: What's absent that would prevent this class of failure?

| Missing | What it would prevent | Severity |
|---------|----------------------|----------|
| No mechanism to express "wait for this specific side effect" in the test framework | Every async test is a race condition; this test is just the first one slow enough to fail visibly | Critical |
| No distinction between "test the logic" and "test the integration" in the test suite | Async integration tests run with the same expectations as synchronous unit tests | Significant |
| No test infrastructure documentation on async testing patterns | Each developer invents their own approach to testing async flows | Significant |

### Layer 2: The assumption that rotted

**"Processing is fast enough"** — this was an inherited assumption from when
the system was a monolith with in-process event handling. The migration to
a message queue (8 months ago) changed the processing model from synchronous
to asynchronous, but nobody updated the test infrastructure's assumptions.

The test was correct when written. The system changed around it. The assumption
rotted.

**Fragility**: This assumption gets more fragile with every async feature the
team ships. The "flaky" tests are accumulating because the test infrastructure
has no concept of eventual consistency.

### Layer 3: The debugging frame is the problem

**Synthesis (2→3)**: Layer 1 showed the system lacks async-aware test
infrastructure, retry mechanisms, and consistency guarantees. Layer 2
showed the root assumption — "processing is fast enough" — rotted when
the system migrated from sync to async. Ask: what frame makes all of
this invisible? The "flaky test" frame. Inside that frame, the test is
the problem and the system is fine. The frame structurally prevents the
team from hearing what the test is telling them.

**Frame the team is using**: "This is a flaky test" — a test reliability problem.

**What this frame illuminates**: Retries, CI stability, test quarantine.

**What this frame structurally excludes**: The possibility that the test is
working correctly — it's accurately detecting that the system has a race
condition. The "flaky" label is the team's way of not hearing what the test
is telling them.

**The frame mismatch**: The team is debugging the TEST. The test is revealing
a property of the SYSTEM. The system has no mechanism to guarantee that async
side effects complete before dependent operations execute. This isn't a test
problem — it's an architectural absence.

### Layer 4: The structural intervention

**Synthesis (3→4)**: Layer 3 revealed the "flaky test" frame hides a
system-level absence: no concept of eventual consistency in test
infrastructure. Ask: what is this system *trying to become*? It already
migrated to async processing but its surrounding infrastructure (tests,
monitoring, error handling) hasn't followed. The latent design: an
async-aware test and observability layer that treats eventual consistency
as a first-class system property.

**Pattern in the negative space**: Every finding points to the same absence —
the system migrated from synchronous to asynchronous processing but the
surrounding infrastructure (tests, monitoring, error handling) still assumes
synchronous cause-and-effect.

**Minimum viable intervention**: Introduce an async-aware test primitive —
a `wait_for_condition(predicate, timeout)` utility that polls for a side
effect rather than asserting immediately. Apply it to this test and the
12 other tests currently marked "flaky." This doesn't fix the system's
deeper eventual-consistency gaps, but it makes the test suite capable
of accurately testing async behavior, which will reveal the real bugs
hiding behind the "flaky" label.

**What to resist**: Don't add retries. Retries are a way of not listening
to what the tests are saying. Don't increase timeouts globally. Don't
quarantine the tests. These are all ways of suppressing the signal.

### The diagnostic oh-shit moment

> "You don't have flaky tests. You have a system that migrated to async
> processing without migrating its verification infrastructure. Every
> async feature you've shipped in the last 8 months is undertested. The
> tests you've marked 'flaky' are the only ones honest enough to tell
> you."

---

## Worked Example: Memory Leak in Production

### The Symptom
Memory usage on the API servers grows ~2% per hour under normal load.
Restarts every 12 hours keep it manageable. The team has been living with
this for two months.

### Step D: Diagnostic Intake

**Assumption chain** (what must be true for memory to be stable):
1. Resources allocated during request handling are freed after the response
2. Long-lived connections (WebSockets) clean up when clients disconnect
3. Caches have eviction policies
4. Background jobs release references when complete

**Where the chain breaks**: Investigation reveals WebSocket connections.
The connection handler allocates per-connection state (user context, subscription
list, message buffer). The cleanup path assumes `onClose` fires when the client
disconnects.

**The gap**: `onClose` fires for clean disconnects. For network drops, stale
connections, or mobile devices that lose signal — the connection object persists.
No timeout, no heartbeat, no reaper.

### Layer 1: What's absent that would prevent this class of failure?

| Missing | What it would prevent | Severity |
|---------|----------------------|----------|
| No connection lifecycle manager (heartbeat + timeout + reaper) | Stale connections accumulate indefinitely; every long-lived connection feature will exhibit this pattern | Critical |
| No metric for "resources held by idle connections" | The monitoring stack tracks request latency and error rates but is blind to resource lifecycle; the leak is invisible to the dashboard | Critical |
| No load test that simulates ungraceful disconnects | The test suite only tests the happy path (connect, use, disconnect cleanly); the failure mode is untested | Significant |

### Layer 2: The assumption that rotted

**"Clients disconnect cleanly"** — inherited from the HTTP request/response
model. HTTP connections are short-lived and stateless; cleanup is trivial.
WebSockets are long-lived and stateful. The team added WebSocket support
6 months ago but the system's resource management model still assumes
HTTP's lifecycle semantics.

This is an inherited assumption that became load-bearing when the connection
model changed. Nobody decided "we don't need connection lifecycle management."
It was simply never considered because the HTTP frame didn't require it.

### Layer 3: Frame mismatch

**Synthesis (2→3)**: Layer 1 showed no heartbeat, no reaper, no metric for
idle resources. Layer 2 showed the "clients disconnect cleanly" assumption
was inherited from HTTP and never updated for WebSockets. Ask: what frame
makes all of this invisible? The "memory leak" frame. Inside that frame,
you profile the heap and look for retained objects. But every object here
IS reachable — the garbage collector is working correctly. The frame
prevents the team from seeing that the problem is definitional, not
mechanical: the system has no concept of "dead connection."

**Frame the team is using**: "Memory leak" — a resource management problem
in the application code.

**What this frame illuminates**: Heap profiling, object retention, garbage
collection tuning.

**What this frame excludes**: The possibility that this isn't a leak in the
traditional sense. Every object IS reachable — it's held by a live connection
object. The garbage collector is working correctly. The problem is that the
system has no definition of "this connection is dead" for non-clean disconnects.

**The deeper frame problem**: The system has no concept of **resource ownership
with timeout**. It can allocate resources and free them on explicit signal.
It cannot reclaim resources when the signal never comes. This is a
category-level absence — not specific to WebSockets.

### Layer 4: The structural intervention

**Synthesis (3→4)**: Layer 3 revealed the system lacks "resource ownership
with timeout" — a category-level absence, not WebSocket-specific. Ask:
what is this system trying to become? It moved from request-scoped to
connection-scoped resources but never built the lifecycle primitive that
connection-scoped resources require. The latent design: a resource
lifecycle manager that works for any long-lived resource, not just
WebSockets.

**Pattern**: The system was designed for request-scoped resources (allocate,
use, free — all within one request). It now has connection-scoped resources
but no connection-scoped lifecycle management.

**Minimum viable intervention**: Add a connection reaper — a background
process that periodically checks connection liveness (heartbeat/ping) and
cleans up stale connections. Add a metric for "live connections" and
"connection age distribution" so the monitoring stack can see resource
lifecycle, not just request throughput.

**What to resist**: Don't just fix WebSockets. The structural absence
(no lifecycle management for long-lived resources) will manifest again
with the next long-lived resource: SSE streams, background uploads,
persistent subscriptions. Build the lifecycle primitive, not just
the WebSocket fix.

### The diagnostic oh-shit moment

> "You don't have a memory leak. You have a system that was designed for
> a world where every interaction is a short-lived request, and you've
> introduced long-lived connections without introducing the concept of
> 'a connection that should end but didn't say so.' The 12-hour restart
> cycle isn't a workaround — it's your system's only lifecycle management
> mechanism, and it's doing the job that a connection reaper should be
> doing."

---

## Worked Example: Data Inconsistency Across Services

### The Symptom
Customer support reports that user profile changes (name, email) sometimes
"don't stick." Users update their profile in the web app, see the change,
but emails still go to the old address. Happens ~2% of the time, no
pattern to which users.

### Step D: Diagnostic Intake

**Assumption chain**:
1. User updates profile via web app → Profile Service writes to database
2. Profile Service publishes `UserUpdated` event
3. Email Service consumes event, updates its local copy of user email
4. Next email uses the updated address

**Where the chain breaks**: Investigation reveals the event is published
BEFORE the database transaction commits. If the transaction fails or is
slow, the Email Service receives an event for a change that hasn't
persisted yet — or it reads the old value when it queries for enrichment
data.

### Layer 1: What's absent?

| Missing | What it would prevent | Severity |
|---------|----------------------|----------|
| No transactional outbox pattern — events published outside the transaction boundary | Any event consumer can act on data that isn't committed yet; the profile case is just the visible instance | Critical |
| No event ordering or idempotency guarantee | If events arrive out of order or are replayed, consumers can overwrite new data with old data | Critical |
| No reconciliation mechanism between services | When drift happens, there's no way to detect or correct it except customer complaints | Significant |

### Layer 2: Assumptions

**"Event publishing and database commits are effectively simultaneous"**
— This is an invisible assumption. The code publishes the event in the
same method that commits the transaction, so it LOOKS atomic. But it's
two independent operations with no transactional guarantee. This is the
classic dual-write problem, and the team doesn't know they have it
because the code's structure disguises it.

**"Each service's local copy stays consistent with the source"** — There
is no mechanism to verify this. No checksums, no version vectors, no
periodic reconciliation. Consistency is assumed, never checked. The
system has no way to know it's inconsistent except when a human notices.

### Layer 3: Frame mismatch

**Synthesis (2→3)**: Layer 1 showed no transactional outbox, no ordering
guarantees, no reconciliation. Layer 2 showed two invisible assumptions:
"event publishing and database commits are simultaneous" and "consistency
is emergent." Ask: what frame makes all of this invisible? The
"event-driven microservices" frame. Inside that frame, loose coupling
is the goal and consistency is assumed to emerge from correct event
handling. The frame structurally excludes distributed consistency as
something that requires explicit mechanisms.

**Frame**: "Event-driven microservices" — services communicate via events,
each owns its data.

**What this frame illuminates**: Loose coupling, independent deployment,
service autonomy.

**What this frame structurally excludes**: Distributed consistency as a
first-class concern. The event-driven frame treats consistency as an
emergent property ("if everyone handles events correctly, the system
is consistent"). But consistency doesn't emerge — it requires explicit
mechanisms: transactional outbox, event ordering, version vectors,
reconciliation loops.

The team adopted the microservices frame but not the distributed systems
discipline that frame requires. They have the architecture of a
distributed system with the consistency assumptions of a monolith.

### Layer 4: The structural intervention

**Synthesis (3→4)**: Layer 3 revealed the team adopted the microservices
architecture without the distributed systems discipline it requires.
Ask: what is this system trying to become? It wants event-driven autonomy
but needs transactional consistency at the boundaries. The latent design
is not a new architecture — it's the missing transactional boundary
that makes the current architecture actually work.

**Minimum viable intervention**: Implement a transactional outbox for
the Profile Service. Events are written to an outbox table within the
same database transaction as the data change, then published by a
separate relay process. This guarantees events reflect committed data.

Then add a nightly reconciliation job that compares email addresses
across Profile Service and Email Service, flagging drift.

**What to resist**: Don't build a distributed saga framework. Don't
introduce event sourcing. The problem is a missing transactional
boundary, not a missing architecture. Fix the boundary.

### The diagnostic oh-shit moment

> "This isn't a bug in your profile update flow. Your system has the
> architecture of a distributed system with the consistency model of
> a monolith. You assumed consistency would emerge from correct event
> handling, but you have no mechanism to guarantee events reflect
> committed state, no way to detect when services drift apart, and no
> way to correct drift when it happens. The profile bug is the 2% of
> cases where the gap is visible. The other 98% are drifting too —
> you just haven't noticed yet because nobody's complained."

---

## Quick Diagnostic Questions for Any Bug

When you don't have time for full diagnostic analysis, ask these five
questions. Each one targets a different structural absence:

1. **"Is this a bug or a message?"**
   Is the system trying to tell you something about itself? Is the
   failure revealing a structural property you haven't been able to see?

2. **"What would make this bug IMPOSSIBLE, not just unlikely?"**
   Not "what check would catch it" but "what invariant enforcement would
   prevent this entire class of failure?"

3. **"When was this code last correct?"**
   If it was once correct, what changed in the system around it? The bug
   might not be in the code — it might be in the assumption that rotted.

4. **"What are this bug's siblings?"**
   If the structural absence exists, what other failures does it enable?
   What bugs haven't manifested yet but share the same structural cause?

5. **"Why didn't the system catch this?"**
   What monitoring, test, type check, or architectural guardrail is
   absent that would have prevented this from reaching production?
