# Strategy & Design Artifact Examples

## Worked Example: Product Launch Plan

### The Artifact
A product team's launch plan for a new collaboration feature. Covers timeline,
marketing plan, success metrics (DAU, retention), engineering milestones, and
a competitive analysis section.

### Layer 1: Absence Inventory (Top 5)

1. **No failure criteria defined** — Success metrics exist, but there's no
   "at what point do we kill this?" threshold. Without failure criteria,
   zombie features live forever. (Critical)

2. **No cannibalization analysis** — New feature overlaps with existing workflow.
   Plan measures new feature adoption but not whether it drains usage from
   the existing feature, potentially making overall product worse. (Critical)

3. **No capacity plan for support** — Launch plan covers marketing and engineering
   but not customer support staffing for the confusion/bug-report spike that
   accompanies every launch. (Significant)

4. **No rollback plan** — If the feature causes severe issues post-launch,
   there's no documented path to disable or roll back without data loss. (Significant)

5. **No plan for partial adoption** — Success is modeled as binary (users adopt or don't).
   No strategy for the likely middle state: some team members adopt, others don't,
   creating workflow friction. (Minor)

### Layer 2: Load-Bearing Assumptions

**"Users want collaboration; they just lack the tool"**
- This is a solution-first assumption. The plan doesn't cite user research
  showing collaboration is a pain point — it assumes it from competitive pressure.
- Fragility: High. If users chose this product because it's individual-focused,
  adding collaboration may weaken the core value prop.
- Validate: Run a demand signal study before building.

**"DAU is the right success metric"**
- DAU measures frequency but not depth or satisfaction. A feature users
  visit daily because it's confusing scores high on DAU.
- Fragility: Moderate. The metric might celebrate the wrong outcome.
- Hedge: Add a quality metric (task completion rate, or CSAT on the feature).

**"The competitive landscape stays the same through the launch window"**
- The 6-month timeline assumes competitors don't ship something similar first.
- Fragility: Moderate, depends on competitive intelligence.
- Hedge: Define a speed-to-market threshold that would change the plan.

### Layer 3: Frame Exclusions

**Synthesis (2→3)**: Layers 1–2 surfaced: no failure criteria, no
cannibalization analysis, no rollback plan, and assumptions that "users want
collaboration" (unvalidated), "DAU is the right metric" (measures frequency
not quality), and "competitive landscape stays static." Ask: what single
frame makes all of these invisible? The answer: the feature-launch playbook.
Inside a playbook, the decision to build is already made — so failure
criteria, demand validation, and premise-questioning are structurally
out of scope. The playbook only asks "how" and "when," never "whether."

**Frame**: Feature-launch playbook (timeline → build → market → measure).

**Illuminates**: Execution clarity, team coordination, measurable outcomes.

**Structurally excludes**:
- Whether to build this at all (the playbook starts after the decision)
- Non-feature alternatives (e.g., partnerships, integrations, workflow education)
- Systemic effects on the product ecosystem (how this feature changes the
  meaning and usage of adjacent features)

**Alternative frame**: Jobs-to-be-done analysis would ask "what job are users
hiring our product for?" before assuming collaboration is the answer.

**Recommendation**: Insert a "strategic rationale" section that explicitly
justifies why this is a feature build and not an integration/partnership,
and what user evidence supports the bet.

### Layer 4: Via Negativa Design

**Synthesis (3→4)**: Layer 3 showed the playbook frame excludes the
question "whether to build this at all" and has no mechanism for
self-correction. Ask: what is this plan *trying to become* that the
playbook frame won't let it? It's trying to be a plan that can change
its own mind — a learning plan. The cluster of absences (no failure
criteria, no demand validation, no conviction checkpoints) all point
at the same latent design.

**Pattern in the negative space**: The absences cluster around "the plan
doesn't question its own premise." There's strong execution planning
but no mechanism for the plan to update itself based on new information.

**Latent design**: This launch plan wants to be a *learning plan* — one
that includes checkpoints where the team asks "is this still the right thing
to build?" not just "are we on schedule?"

**Minimum viable intervention**: Add three "conviction checkpoints" to the
timeline — moments where the team reviews demand signals and decides whether
to continue, pivot scope, or stop.

**Resist adding**: Don't add exhaustive scenario planning. The plan needs
self-questioning mechanics, not more contingency branches.

---

## Worked Example: Architecture Decision Record (ADR)

### The Artifact
ADR proposing a microservices migration from a monolith. Cites scaling needs,
team autonomy, and deployment independence as motivations.

### Layer 2 (jumping straight to the high-value layer):

**"Team boundaries map cleanly to service boundaries"**
- The ADR assumes Conway's Law works in their favor. If teams are
  cross-functional and share ownership of business domains, service
  boundaries will create coordination overhead, not reduce it.
- Fragility: Depends entirely on org structure, which isn't described.

**"The monolith's problems are caused by being a monolith"**
- Maybe. Or maybe the problems are caused by poor modularity within
  the monolith, which will be replicated in the microservices as
  poor API contracts. Microservices don't automatically fix architecture
  problems; they distribute them.

**"Operational maturity exists to run distributed systems"**
- Microservices require sophisticated observability, deployment pipelines,
  and incident response. The ADR doesn't assess whether the team has these.
  If not, the migration will trade application complexity for operational complexity.

### Layer 3: Frame Exclusion

**Frame**: Microservices vs. monolith (binary architectural choice).

**Excludes**: The entire middle ground — modular monolith, service-oriented
architecture without full microservices, domain-driven design within
a monolith, or even "fix the monolith's internal boundaries first."

The framing as a binary choice forecloses the most pragmatic options.

---

## Quick Diagnostic Questions for Any Strategy Artifact

1. **Where are the failure criteria?** (If absent, success is unfalsifiable)
2. **What would make this the wrong bet?** (Tests assumption awareness)
3. **Who loses if this succeeds?** (Surfaces second-order effects)
4. **What would a skeptic with full context say?** (Steel-mans opposition)
5. **Was this approach chosen or defaulted to?** (Frame awareness)
