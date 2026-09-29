# Working brief v0

Purpose: reduce repeated overnight HIGH pages without losing newly returned problems. Offline stdlib prototype, explain all record-level changes, no deployment.
Evidence: the three public files; captures are synthetic and independent, in delivery order, t is receipt time. User explicitly identifies quick_return as two real problems. Capture names are informal. No evidence yet about source-counter semantics or what ports physically identify.
Obstruction: time since last page conflates continuation and recurrence. Raising 20 to 60 suppresses long-4 but still suppresses quick-4.
Routes: (A) retain cooldown with sensitivity 20/60; (B) alert on episode onset, track reset by a NORMAL observation; (C) later separate accepted source evidence from delivery rows if counter semantics permit.
Candidate v0 implements A/B only; cabinet and port scopes are rival lossy abstractions. INVALID preserving an active episode and HIGH at startup paging are provisional policies. No source-order filtering yet. A cabinet scalar can wrongly let one port's NORMAL clear another port's HIGH; this is a known transfer obligation, not a finished candidate.
Return criteria: explicit state model, runnable before/after traces, generated histories exposing scope, ordering, reset, and unreadability assumptions. Tests cannot establish technician preference or physical truth.
