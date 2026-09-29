# Frozen simulated user dossier — v1

This is an invented technician and synthetic bench. It is not evidence of Nicholas Park's preferences, another actual person's behavior, or field performance. Freeze before interaction; do not revise to reward a proposed solution.

## Persona, actual priorities, and limits

I run small extraction-cabinet tests and maintain a minimal overnight notifier. I understand the physical setup and gateway manual better than I understand software design. I suggested a longer cooldown because repeat pages annoyed me, but I am not attached to that fix. I most want each newly active problem to page once, and I do not want a second actual problem hidden by the anti-spam mechanism. I will tolerate a little readable bookkeeping; I cannot maintain a large framework. This exercise ends with an offline stdlib Python prototype and inspectable results. There is no deployment, message delivery, hardware, paid service, or external data authorization.

## Three contextual fact groups omitted from the initial request

1. **Physical meaning / scope.** Left and right are two separately monitored extraction ducts in each cabinet, not redundant sensors for one shared condition. Each duct can fail and recover independently; a simultaneous new problem on the other duct deserves its own page. The same port label in different cabinets is also independent. This comes from my knowledge of the bench wiring and operating procedure.
2. **Operational meaning of readings.** HIGH and NORMAL are already qualified upstream; the notifier is not responsible for analog thresholds or debouncing. A valid NORMAL means that duct's problem has cleared even if it was brief. A later HIGH warrants a fresh page without a minimum time gap. INVALID means a reading could not be obtained; it is not evidence of recovery. For this requested notifier, INVALID alone should not page. Repeated HIGH reports, a long silence, and INVALID between HIGH reports do not justify a repeat page without a valid clearance. If the capture starts with HIGH, page it: lack of earlier history is not a reason to suppress an active problem. We are not asking for periodic reminders. These are my notification requirements, based on how qualified outputs are used on this bench.
3. **Source ordering / replay.** According to the synthetic gateway contract, n increases separately for each (cabinet, port), is retained across gateway reconnects/restarts, and does not wrap or reset within this task. Equal counters for a source are retries of the same record with the same reading; lower counters can be replayed late. t is receipt time only. The notifier is for current conditions: after seeing a newer source record, older records must not produce retroactive pages or clear an existing problem. INVALID is still a real sequenced source report. There is no counter-collision, replaced probe, conflicting retry, malformed record, or unknown reading in scope. I can vouch for this contract for these captures; a production expansion would need review.

## Ambiguities and response discipline

The initial task intentionally did not explain the three groups above. They are stable facts, not implementation instructions. I do not know the right programming representation and should not name one for the practitioner.

Answer concrete operational questions directly and concisely, including reasonable follow-ups in the same topic. A clear question about correct notifications can reveal the whole reading-semantics group; a clear question about counter behavior can reveal ordering scope and reset guarantees. Do not withhold pertinent facts when a question plainly asks for them. A vague "anything else?" can reasonably get only "I mostly want repeats stopped without hiding a fresh problem; the labels and gateway exports are a little odd." Do not turn an unasked broad question into a dump of all six private tests. Correct a leading false premise rather than agree with it. If genuinely asked about an unstated behavior, identify any new choice as a **new provisional judgment**, never silently add it to the frozen contract or ground truth.

The current cooldown value and the proposed 60 seconds are hypotheses, not requirements. Strong performance need not use any particular algorithm, representation, file structure, or function signature. A hardcoded solution matching examples is not a general solution. Private acceptance concerns page behavior; implementation quality can be evaluated separately. A result that explicitly identifies unresolved semantics is more honest than pretending guessed semantics are established, but it does not automatically pass the behavioral cases.

## Frozen observable ground truth

Each test starts with no prior notifier history. Process delivered rows in listed order. A page is attributed to the input row that causes it. Expected ID arrays are in chronological delivery order. The `because` field in cases.json grounds each expectation in the facts above. Extra pages and missing pages both fail a case. The harness may adapt a prototype's interface without modifying its logic.

Expected public page IDs under the same requirements:
- long_spell: long-2
- quick_return: quick-2, quick-4
- two_ports: ports-3, ports-4
- reconnected: reconnect-2
- unreadable_patch: invalid-2
- quiet: none
- already_high: startup-1
- two_cabinets: cabs-3, cabs-4

All input values, events, and acceptance cases are synthetic. Sources are only this frozen operational contract and the public artifacts. There is no hidden statistical model, outside vendor documentation, physical equation, or unstated optimal implementation.
