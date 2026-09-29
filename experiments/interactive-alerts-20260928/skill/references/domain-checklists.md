# Domain-Specific Absence Checklists

These are optional accelerators for Layer 1. They supplement the five universal
probes — they don't replace them. Use them when you recognize the artifact type.

---

## Code / Pull Requests
- Unhandled error states and edge cases
- Missing input validation or boundary checks
- Absent tests (unit, integration, edge case, property-based)
- No rollback or recovery path
- Missing logging, observability, or metrics
- Undocumented breaking changes
- Missing migration path for existing users/data
- No performance considerations or benchmarks
- Missing security review (auth, injection, data exposure)

## Git Branches / Commit History
- Commits that are suspiciously large (hiding changes in volume)
- Missing commits between logical steps (gaps in the narrative)
- No branch protection or review requirements documented
- Dead branches with no cleanup strategy
- Missing changelog or release notes
- Commit messages that describe WHAT but not WHY
- No connection between branch work and any ticket/issue

## Architecture / System Design
- Failure modes not addressed
- Scale scenarios not considered (10x, 100x)
- Security boundaries not defined
- No degradation strategy (graceful, partial, circuit-breaking)
- Missing data flow diagram
- No observability strategy
- No disaster recovery or backup plan
- Missing capacity planning

## Visual / UI Artifacts (screenshots, mockups, designs)
- Missing states: empty, loading, error, partial, overflow
- No responsive/mobile consideration
- Accessibility not addressed (contrast, screen reader, keyboard nav)
- Missing interaction states (hover, focus, disabled, active)
- No consideration of internationalization/localization
- Missing content edge cases (long text, missing text, special characters)
- No dark mode / theme consideration
- Missing user feedback for actions (confirmations, progress)

## Data / Datasets
- No schema documentation
- Missing data dictionary (what do the fields mean?)
- No null/missing value handling strategy
- Absent data quality checks or validation rules
- No lineage/provenance tracking
- Missing privacy/PII assessment
- No versioning strategy
- Absent bias or representativeness analysis
- No retention/deletion policy

## Infrastructure / Configuration
- No secrets management strategy
- Missing environment parity documentation (dev vs staging vs prod)
- No backup/restore verification
- Absent monitoring and alerting
- Missing runbook for common failures
- No cost analysis or budget constraints
- Missing network security (firewall rules, VPCs, access controls)
- No capacity planning or auto-scaling configuration

## Email / Communication
- Missing audience consideration (who else should be on this?)
- No clear ask or call to action
- Absent context for recipients who lack background
- Missing deadline or timeline
- No follow-up plan
- Tone mismatch with stakes/relationship
- Missing acknowledgment of the recipient's perspective or constraints
- No consideration of how this reads if forwarded to unintended audience

## Strategy / Business
- Competitors not mentioned
- Failure criteria not defined (only success criteria exist)
- Resource constraints not acknowledged
- Timeline dependencies not mapped
- Stakeholders not identified
- Exit conditions or pivot triggers absent
- No second-order effects analysis
- Missing sensitivity analysis (what if assumptions are wrong by 20%?)
- No consideration of regulatory or compliance landscape

## Writing / Ideas / Essays
- Counterarguments not addressed
- Key terms not defined
- Audience not specified
- Scope boundaries not drawn
- Evidence gaps or unsubstantiated claims
- Missing acknowledgment of limitations
- No consideration of who this argument might harm or exclude
- Missing "so what?" — why this matters to the reader

## Processes / Workflows
- No owner or accountable person defined
- Missing exception handling (what happens when the process breaks?)
- No measurement or feedback mechanism
- Absent onboarding path (how does a new person learn this?)
- Missing handoff points between people/teams
- No sunset criteria (when does this process end or get revisited?)
- Missing documentation of tribal knowledge embedded in the process
- No consideration of what happens during vacations/departures
