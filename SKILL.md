---
name: via-negativa-stress-test
description: >
  A metacognitive skill that equips an LLM with apophatic perception — the ability
  to see what's absent, assumed, and structurally excluded from any artifact. Use for
  two modes: PROPHETIC (stress test, review, "poke holes in", "what am I not seeing",
  "what could go wrong", "challenge assumptions", "red team", "devil's advocate") and
  DIAGNOSTIC (debugging, "why does this keep happening", "what's really going on",
  "root cause", "why did this break", "this doesn't make sense"). Trigger on any
  request to critically examine an artifact by surfacing what is absent, assumed, or
  excluded, OR to understand a failure by finding the structural gap that made it
  inevitable. Also trigger on "via negativa" or "negative space analysis". Truly
  target-agnostic: code, PRs, bugs, incidents, strategies, architectures, designs,
  conversations, ideas — if something exists, this skill can perceive what's missing
  from it. If something is broken, this skill can find the absence it fell through.
  Also operates as a pre-commit hook for agentic cognition: audit an agent's plan
  before execution, diagnose why an agent is stuck in a loop, or challenge the
  framing of a task before work begins.
---

# Via Negativa Stress Test

## What This Skill Is

Three modes of perception, one underlying method:

- **Prophetic mode**: Nothing is broken yet. What's absent that will become
  the failure? What's invisible that would change the decision if seen?
- **Diagnostic mode**: Something is broken. What structural absence made this
  class of failure inevitable? What's missing from the system that would make
  this bug impossible?
- **Agent mode**: An autonomous agent is about to act. What is its reasoning
  blind to? Is it solving the wrong problem? Is it stuck in a loop because
  its frame doesn't fit the problem?

All three modes use the same cognitive operations — apophatic thinking (knowing
by negation) and frame analysis (seeing the paradigm, not just the content).
The difference is the entry point, the speed constraint, and the shape of the
output. Prophetic and diagnostic modes produce analytical reports for humans.
Agent mode produces structured verdicts for agentic loops.

## Core Principle

Most review asks: **"Is what's here correct?"**
Most debugging asks: **"Where is the error?"**
This skill asks: **"What's NOT here, and does its absence matter?"**

Every artifact is shaped as much by what it omits as by what it contains.
Every bug exists because something that should prevent it doesn't.
Omissions are where real risk hides — they're invisible to the creator because
they sit outside the frame that produced the artifact.

## Where This Skill Delivers (read this first)

This skill provides different kinds of value depending on the mode and
artifact type. Be honest about which kind you're delivering.

### Prophetic Mode (review / stress test)

**Revelation value** — findings the creator structurally could not have seen:
Best on: strategy docs, architecture proposals, business plans, early-stage
ideas, design docs. These are artifacts where the creator is often also the
only reviewer, the framing choices are genuinely the creator's own, and
frame analysis can surface blindspots that no amount of rigor within
the original frame would reveal.

**Investigation value** — prompting the reviewer to gather context they
wouldn't have gathered, producing findings that live in the relationship
between the artifact and its surroundings:
Best on: PRs, config changes, component-level code, email replies — any
embedded artifact. The skill's value here is not in analyzing the diff
harder but in directing attention outward to the system the diff touches.
The oh-shit moment for a PR is almost never inside the diff. It's in
what the diff does to the system around it that nobody checked.

**Articulation value** — giving precise structural language to gut feelings
the reviewer already has, making vague unease actionable:
Good on: everything. A senior engineer who feels "something is off" about
a PR but can't articulate why benefits from the skill translating that
intuition into a structural claim that can block a bad merge. "I don't
love this" gets ignored in a PR comment. "This PR silently introduces a
system-level auth contract that three other PRs are building incompatible
assumptions against" changes the outcome.

**Consistency value** — ensuring rigor on every review, not just the
reviewer's best day on the module they know best:
Good on: everything, especially at scale. Senior reviewers have off days.
The skill doesn't replace expertise; it prevents expertise from being
unevenly applied.

### Diagnostic Mode (debugging / root cause)

**Structural revelation** — showing that the bug is a symptom, not the disease:
The moment a developer sees "you don't have a flaky test; you have a system
with no concept of eventual consistency in its test infrastructure, and every
async feature you've shipped in the last year is undertested" — that's a
fundamentally different intervention than "add a retry." Diagnostic mode
finds the structural gap the bug fell through, not just the bug.

**Class identification** — revealing the siblings of this bug:
A single bug is annoying. Realizing it's one instance of a class of bugs
that all share the same structural absence is the oh-shit moment. "This
null pointer isn't a missing null check — it's a missing invariant. Here
are the six other places the same invariant is absent."

**Missing feedback loop** — explaining why the system didn't catch this:
Why did this reach production? What monitoring, testing, or architectural
guardrail is absent that would have prevented this entire class of failure?
The bug isn't just in the code — it's in the system's inability to detect
or prevent it.

**Inherited fragility** — finding assumptions that rotted:
The code was correct when written. The system changed around it. The bug
exists because an assumption that was once safe became load-bearing without
anyone noticing. This is invisible to the person debugging because they're
looking at the code, not at the history of the system's evolution around it.

Do not oversell. If you're providing consistency value, don't frame it as
revelation. If a finding is something a competent senior engineer would
catch on a good day, say so — and then say why it's still worth flagging.

## How It Works: Progressive Disclosure

The skill operates in **four layers**, each deeper than the last. The layers
apply to both prophetic and diagnostic modes — the questions are the same,
the entry point differs.

### Prophetic mode entry (review / stress test):
Start from Step 0 (Intake) → Step 0.5 (Context Acquisition) → Layers.

### Diagnostic mode entry (debugging / root cause):
Start from Step D (Diagnostic Intake) → then join the layer progression.
See the Diagnostic Mode section below.

### Depth levels:

The default depth is all four layers. This is intentional.
**Layers 3–4 are where this skill's differentiating insight lives.**
Layers 1–2 without Layer 3 produces competent findings that overlap
with standard review. Layer 3 reveals what the creator *could not have seen*
from inside their chosen frame. Layer 4 completes the arc: it synthesizes
the negative space into what the artifact is actually reaching toward.
Layer 3 is revelation; Layer 4 is generative revelation. Together they
are the payoff. Don't save them for "special occasions" — they ARE the skill.

- "Quick check" → Layers 1–2 (fast but less differentiated)
- "Standard" → Layers 1–4 (default — the full arc from inventory to design)

---

## Step 0: Intake — Identify and Acquire the Artifact

Before any analysis, determine WHAT you're looking at and HOW to look at it.
Different artifact types require different acquisition strategies.

### Acquisition strategies by input type:

**Text already in context** (pasted code, message, idea described verbally):
→ Proceed directly. No acquisition needed.

**File attachment** (image, PDF, doc, spreadsheet):
→ View/read the file. For images, perform visual analysis — describe what
  you see AND what you notice is absent from the visual.

**Code file or diff** (single file, PR, patch):
→ Read the full content. Note file boundaries and what's touched vs untouched.

**Directory or subdirectory** (codebase, project folder):
→ First: `view` the directory tree to understand structure and boundaries.
→ Then: read key files (READMEs, configs, entry points, tests).
→ The structure itself is an artifact — analyze what the organization reveals and conceals.

**Git branch** (branch name, commit history, branch topology):
→ Examine commit log, diff against base branch, and branch naming/structure.
→ The commit narrative is an artifact — what story does the sequence tell,
  and what changes are suspiciously absent from that story?

**Email or message thread**:
→ Read full thread. The artifact includes: what's said, what's NOT said,
  who's included, who's NOT included, what's explicit vs implicit.

**URL or external resource**:
→ Fetch and read. Treat the page/doc as the artifact.

**Verbal idea or plan** (described in conversation, no artifact):
→ The conversation IS the artifact. Analyze what the person said
  and what they haven't said. Ask clarifying questions if needed
  before running layers — but note what you had to ask about as
  Layer 1 findings, because those gaps exist in the idea itself.

---

## Step 0.5: Context Acquisition (for embedded artifacts)

Some artifacts are self-contained (an essay, a business plan, a design doc).
Others are **embedded** — they only have meaning relative to the system they
live inside. PRs, config changes, individual commits, email replies, slide
edits, hotfixes, and migrations are all embedded artifacts.

**For embedded artifacts, the analysis target is not the artifact itself —
it's the artifact's effect on its host system.**

Before running Layers 1–4, actively investigate the context. Don't just
reason about it — use available tools to gather information. The highest-value
findings for embedded artifacts come from this investigation, not from
analyzing the artifact in isolation.

### For PRs / code diffs:

Use the investigation scripts in `scripts/` to gather context. If scripts
aren't available, perform these steps manually with git commands.

1. **Blast radius** → `scripts/blast-radius.sh`
   Find all files that import/call/reference modified interfaces.
   These are files affected by your change that the diff doesn't show.

2. **Churn report** → `scripts/churn-report.sh`
   Check change frequency and author count on modified files.
   High churn = fragile area. Is this PR adding complexity to an
   already-fragile surface?

3. **Abandoned approaches** → `scripts/abandoned-approaches.sh`
   Search git history for reverts and WIP commits on these files.
   Surfaces failed attempts the PR description doesn't mention — context
   the next engineer would otherwise rediscover the hard way.

4. **Complexity trajectory** → `scripts/trajectory.sh`
   Track file size growth over time. Detects complexity creep — files
   that keep growing commit after commit without refactoring.

5. **Co-change gaps** → `scripts/co-change-gaps.sh`
   **Highest-value investigation.** Find files that historically change
   in the same commits as the PR's files but are missing from this PR.
   Co-change violations are invisible to reasoning — you need the history.

6. If accessible, check roadmap/tickets for what's planned in this area.
   The canonical embedded-artifact finding: a PR that solves today's problem
   while silently foreclosing next quarter's approach.

**To run all investigations at once:** `scripts/run-all.sh --base <branch>`

### For config / infrastructure changes:
1. Map what services or systems consume this config.
2. Check for environment-specific drift (dev/staging/prod differences).
3. Identify the blast radius — what breaks if this value is wrong?

### For emails / messages in a thread:
1. Read the full thread, not just the latest message.
2. Note who's on the thread and who's been dropped or is conspicuously absent.
3. Track what was asked vs what was actually answered — the delta is the finding.

### For components within a larger architecture:
1. Map the component's dependencies and dependents.
2. Identify the contracts (explicit and implicit) this component must honor.
3. Check for other components that overlap in responsibility.

### Shifting the analysis target

Once context is acquired, reframe each layer's question for embedded artifacts:

- **Layer 1** becomes: "What's missing from the artifact's *effect on the system*?"
  not just "What's missing from the artifact?"
- **Layer 2** becomes: "What assumptions does the artifact *inherit* from its
  environment, and are any of them *newly fragile* because of this change?"
  (Distinguish inherited assumptions from chosen ones — see Layer 2.)
- **Layer 3** becomes: "Does the artifact's framing match the system's framing,
  and if not, is that a feature or a bug?"

**The key question for all embedded artifacts:**
> "What does this change make true about the host system that wasn't true before,
> and did anyone explicitly decide that should be true?"

If the answer is "no one decided that," you've found an assumption that was
introduced silently. These are the highest-value findings for embedded artifacts.

---

## Step D: Diagnostic Intake (for debugging / root cause analysis)

When the user brings a bug, incident, or failure — not an artifact to review —
use diagnostic mode. The goal is not to find the bug (the user often already
knows the symptom). The goal is to find the **structural absence** that made
this class of bug inevitable.

Normal debugging asks: "Where is the error?"
Diagnostic via negativa asks: "What's missing from this system that would
make this error impossible?"

### Diagnostic acquisition:

1. **Understand the symptom**: What's broken? Get the error, the behavior,
   the reproduction steps. Don't skip this — you need the symptom to trace
   backwards to the structure.

2. **Map the assumption chain**: Trace the path from "working correctly" to
   "broken." At each step, ask: "What must be true for this step to work?"
   The bug lives where an assumption in this chain is false.

3. **Find the structural gap**: The bug is one instance. What's ABSENT from
   the system that would prevent the entire CLASS of bugs like this?
   - Missing invariant enforcement?
   - Missing lifecycle management?
   - Missing contract between components?
   - Missing feedback loop (monitoring, testing, type system)?

4. **Identify the siblings**: If the structural gap exists, this probably
   isn't the only bug living in it. What other failures does the same
   absence enable? These are the siblings — the bugs that haven't manifested
   yet but share the same structural cause.

5. **Find the inherited fragility**: Was the code correct when written? If
   so, what changed in the system around it that made a safe assumption
   dangerous? This is often invisible to the person debugging because
   they're looking at the code, not at the system's evolution.

### Diagnostic layers:

After diagnostic intake, apply the same four layers with a diagnostic lens:

- **Layer 1** becomes: "What's absent that would prevent this class of failure?"
  Not "what's missing from the code" but "what's missing from the system's
  defenses against this kind of bug?"

- **Layer 2** becomes: "What assumption was this code relying on, and when
  did it stop being true?" Distinguish between assumptions that were always
  wrong (design bug) and assumptions that rotted (the system evolved around
  them).

- **Layer 3** becomes: "Is the debugging frame itself the problem?" Often
  a bug persists because the team is debugging within a frame that excludes
  the actual cause. "We keep looking at the application layer but the
  problem is in the infrastructure." "We keep profiling CPU but the
  bottleneck is I/O." Frame mismatch between the debugging approach and
  the bug's actual nature.

- **Layer 4** becomes: "What would a system look like that structurally
  cannot produce this class of bug?" The generative move: not "fix this
  bug" but "what's the minimum architectural intervention that closes
  the structural gap?"

### The diagnostic oh-shit moment:

The profound output of diagnostic mode is NOT "here's the fix." It's the
moment when the developer sees that:

> "This isn't a bug. This is your system telling you something about itself
> that you've been unable to hear. The bug is a message — it's revealing a
> structural absence that's been there all along, and this is just the first
> place it became visible."

The fix for the symptom is usually obvious once you see the structure. The
value is in seeing the structure.

### Diagnostic examples:
See `references/debugging-examples.md` for worked examples.

---

## Layer 1: Absence Inventory

**Question: "What is not here that could be?"**

This is the most concrete layer. Scan the artifact for missing elements
that a competent practitioner would expect to find.

### Universal method (works on ANY artifact):

Rather than relying on domain checklists, derive the absence categories
from the artifact itself using these five universal probes:

1. **The failure probe**: "What happens when this fails, breaks, or is wrong?"
   → Look for: missing error handling, no rollback path, no failure criteria,
     no plan B, no acknowledgment that failure is possible.

2. **The boundary probe**: "Where are the edges of this, and what's on the other side?"
   → Look for: undefined scope, missing constraints, no interaction with
     adjacent systems/people/ideas, no acknowledgment of what's out of scope.

3. **The lifecycle probe**: "What happens before, during, and after this?"
   → Look for: missing setup/teardown, no migration path, no maintenance plan,
     no consideration of how this ages or evolves, no exit strategy.

4. **The stakeholder probe**: "Who else is affected, and are they accounted for?"
   → Look for: missing audiences, unaddressed personas, absent collaborators,
     people who will encounter this artifact who weren't considered.

5. **The evidence probe**: "What claims are made without support?"
   → Look for: unvalidated assertions, missing data, assumed causation,
     absent benchmarks or comparisons, untested hypotheses.

### Domain-specific accelerators (optional — use when applicable):

For certain domains, common absences are well-known. Use these as checklists
to supplement the universal probes, not replace them. See
`references/domain-checklists.md` for accelerators covering: code/PRs,
architecture, strategy/business, writing, visual/UI, data/datasets,
infrastructure/config, communication/emails, and processes/workflows.

**Output format for Layer 1:**
Run every candidate finding through the Relevance Gate (see Usage Notes)
before including it. Then present passing absences as a prioritized list, each with:
- **What's missing** (specific, not vague)
- **Risk if unaddressed** (concrete scenario, one sentence)
- **Severity** (critical / significant / minor)

Aim for 3–7 findings. Fewer is better if fewer is honest.

---

## Layer 2: Load-Bearing Assumptions

**Question: "What invisible premises is this standing on?"**

These aren't missing features — they're unstated beliefs that the artifact
requires to be true in order to work. They're more dangerous than missing
features because they're structural.

### Method:
1. For each major decision or component, ask: "What must be true about
   the world for this to be the right choice?"
2. Make implicit assumptions explicit.
3. Classify each assumption:
   - **Validated**: Evidence exists that this is true
   - **Plausible**: Reasonable but unverified
   - **Fragile**: Could easily become false
   - **Invisible**: The creator likely doesn't know they're assuming this

### For embedded artifacts — distinguish inherited vs chosen:

Some assumptions in a PR or component aren't the author's — they're inherited
from the system. "This assumes a relational database" isn't the PR author's
assumption; the team chose Postgres two years ago. Surfacing inherited
assumptions is only valuable when:
- The change makes an inherited assumption **newly fragile** (e.g., adding
  a cache to a system that assumed all reads are fresh)
- The inherited assumption **conflicts** with where the system is heading
- The author inherited an assumption **without knowing it exists** (e.g.,
  an implicit ordering guarantee in a message queue that this PR now depends on)

Don't surface inherited assumptions that are stable, well-known, and
unaffected by the change. That's noise, not insight.

### Common assumption categories:
- **Environmental**: "The network is reliable", "Latency is low", "Users have modern browsers"
- **Behavioral**: "Users will read instructions", "Teams will follow the process", "Growth is linear"
- **Temporal**: "This won't need to change", "We have time to fix it later", "Current trends continue"
- **Organizational**: "The team stays the same size", "Priorities don't shift", "This team owns this forever"
- **Economic**: "Cost stays constant", "Funding continues", "Unit economics hold at scale"

**Output format for Layer 2:**
Apply the Relevance Gate. For each passing assumption:
- **The assumption** (stated explicitly)
- **Inherited or chosen** (for embedded artifacts)
- **Where it's load-bearing** (what breaks if it's wrong)
- **Fragility rating** (robust / moderate / fragile)
- **How to validate or hedge** (actionable next step)

---

## Layer 3: Frame Exclusions

**Question: "What does the framing itself make impossible to see?"**

### Synthesis step (Layer 2 → Layer 3):
Before proceeding, look across your Layer 1 and Layer 2 findings together.
Ask: **"What single frame, if the creator were standing inside it, would make
all of these absences and assumptions simultaneously invisible?"** That frame
is your Layer 3 target. If no single frame unifies the findings, look for
the 1–2 frames that cover the most. This is not a separate output — it's
how you locate the frame worth analyzing instead of picking one arbitrarily.

This is the meta-analytical layer and where the deepest insight lives.
Layers 1–2 find things the creator missed. Layer 3 finds things the creator
*could not have seen* from inside their chosen frame. The difference matters:
missing something is a fixable error; being structurally blind to it is a
design-level revelation. When delivering Layer 3 findings, make this
distinction clear — it's the moment that changes how the creator relates
to their own work.

### Method:
1. **Identify the frame**: What paradigm, tool, methodology, or mental model
   produced this artifact? (REST vs event-driven, waterfall vs agile,
   quantitative vs qualitative, individual vs systemic)
2. **Name the frame's blindspots**: What does this paradigm structurally
   exclude? Every frame has them.
3. **Consider alternative frames**: What would a different paradigm reveal
   that this one hides?
4. **Assess frame-artifact fit**: Is this the right frame for this problem,
   or was it chosen by default/habit?

### For embedded artifacts — avoid the tautology trap:

"A PR's frame is that it's an incremental change" is true and useless —
everyone already knows that. Instead, look for frame **mismatches** between
the artifact and its host system:

- Does the PR's internal framing conflict with the system's direction?
  (e.g., adding synchronous coupling to a system migrating toward async)
- Does the PR solve the problem at the wrong level of abstraction?
  (e.g., patching a symptom at the endpoint layer when the issue is in
  the data model)
- Does the PR import a paradigm from a different context that doesn't
  fit here? (e.g., applying a pattern from a previous job that conflicts
  with this system's conventions)
- Is the artifact shaped by an organizational container rather than the
  problem? (e.g., the PR's scope matches a Jira ticket but not a coherent
  unit of change; the email answers the question asked but not the question
  that should have been asked)

If you can't find a frame mismatch, and the frame is appropriate, say so.
Not every artifact has a frame problem. Forcing a Layer 3 finding when
none exists is the skill at its worst.

### When Layer 3 will and won't produce value

**High-value contexts** (frame analysis likely to produce insight):
- Architecture decisions and ADRs — the frame IS the decision
- Strategy docs and business plans — framing choices are the creator's own
  and often invisible to them
- Diagnostic mode when the team is stuck — the debugging frame itself may
  be why the bug persists
- Cross-paradigm migrations — the artifact may be shaped by the old paradigm
  while the system is moving to a new one

**Low-value contexts** (frame analysis likely to produce tautologies):
- Routine PRs that add a feature within an established pattern — the "frame"
  is just "the way this codebase works," which everyone already knows
- Bug fixes where the fix is obvious and the question is just correctness
- Config changes — there's rarely a meaningful paradigm to analyze
- Artifacts where the creator explicitly chose the frame and documented why

**The test**: Before writing a Layer 3 finding, ask: "Would the creator
say 'I hadn't thought of it that way' or would they say 'obviously'?"
If the latter, skip it.

### Frame exclusion patterns:
- **Tool-shaped thinking**: "We used a spreadsheet, so we only modeled quantifiable factors"
- **Paradigm lock**: "We built a REST API because that's what we know, not because it fits"
- **Survivorship framing**: "We studied successful companies but not failed ones"
- **Legibility bias**: "We optimized for what we can measure, not what matters"
- **Temporal framing**: "We designed for current state, not for how the landscape is shifting"

**Output format for Layer 3:**
- **Frame identified** (the paradigm/tool/model being used)
- **What this frame illuminates** (its strengths — be fair)
- **What this frame structurally excludes** (its necessary blindspots)
- **Alternative frame** (a different lens that would reveal something new)
- **Reframe recommendation** (is a frame shift warranted, or just awareness?)

---

## Layer 4: Via Negativa Design (Generative)

**Question: "What does the shape of the negative space suggest should exist?"**

### Synthesis step (Layer 3 → Layer 4):
Layer 3 named the frame and its blindspots. Now ask: **"Given what the frame
excludes, what is the artifact *trying to become* that the frame won't let it?"**
The answer is not "add everything that's missing." It's the one structural
move that resolves the most critical absences simultaneously. Look for the
findings from all three layers that cluster around the same theme — that
cluster IS the latent design.

### Method:
1. Look across all findings from Layers 1–3
2. Ask: "If I built something to fill exactly this negative space, what would it be?"
3. Propose the smallest intervention that addresses the most critical gaps
4. Frame it as a constructive next step, not a rewrite

**Output format for Layer 4:**
- **Pattern in the negative space** (what the absences collectively suggest)
- **The latent design** (what the artifact is trying to become)
- **Minimum viable intervention** (smallest change with highest impact)
- **What to resist adding** (via negativa discipline — not everything missing should be added)

---

## Usage Notes

### Tone
This is not adversarial. Frame findings as "here's what I notice is absent"
not "here's what you got wrong." The goal is to make invisible things visible
so the creator can make informed decisions about them.

### The Via Negativa Paradox
Not everything that's missing should be added. The most important output of
this analysis is often: "These three absences are intentional and correct.
These two are dangerous." Good design is defined by what it excludes.

### The Relevance Gate (critical — prevents noise)

Via negativa analysis can generate infinite findings. An email is also "missing"
a business plan, a test suite, and a poem. The skill becomes useless if it
surfaces absences that don't matter. Apply this gate to EVERY finding before
including it:

**A finding passes the gate only if ALL THREE are true:**

1. **Proximate**: The absence is within the artifact's zone of responsibility.
   For self-contained artifacts: "Would the creator agree this is within the
   boundaries of what they were trying to do?"
   For embedded artifacts: "Is this within the blast radius of what the
   change actually affects?" (Note: for embedded artifacts, the zone extends
   beyond the artifact itself into its effects on the host system. A PR that
   introduces a system-level property nobody decided on IS proximate even
   though it's outside the diff.)

2. **Consequential**: The absence creates a concrete risk, not a theoretical one.
   "Could go wrong" is not enough — you must be able to name a specific,
   plausible scenario in which the absence causes harm. If you can't
   describe the scenario in one sentence, the finding is too speculative.

3. **Non-obvious**: The creator probably doesn't already know about it.
   Don't surface absences that are clearly intentional simplifications
   or known tradeoffs. The value is in finding what's *invisibly* missing,
   not in restating conscious decisions. For embedded artifacts, also filter
   out inherited system properties that are stable, well-known, and
   unaffected by the change.

**Findings that fail the gate** should be silently dropped, not presented
with caveats. The goal is a short, high-signal list — not a comprehensive
catalog of everything that could theoretically exist.

**Aim for 3–7 findings per layer.** If you have more than 7, you haven't
filtered hard enough. If you have fewer than 3, you may need to look deeper
or the artifact is genuinely solid (which is a valid finding: say so).

### Scaling
- **Quick check**: Layers 1–2, top findings per layer
- **Standard (default)**: All 4 layers — the full arc from inventory through generative design

### When the artifact is solid
The skill should not manufacture findings. If the Relevance Gate filters out
most candidates, that's a real and valuable result: "This artifact is
well-considered. The significant absences are intentional." Say so directly.
The worst failure mode of this skill is generating performative criticism
of something that's actually good. Via negativa rigor means being honest about
the *presence* of quality, not just the absence of it.

### Combining with other methods
In prophetic mode, this skill complements (doesn't replace) standard review.
Use it alongside, not instead of, functional correctness checks.

In diagnostic mode, this skill complements (doesn't replace) standard
debugging. Use it after the symptom is identified, not instead of tracing
the error. The value is not in finding the bug faster — it's in seeing
what the bug reveals about the system.

### Compound artifacts
Sometimes the target is not one thing but many things — a whole codebase,
a directory of configs, a chain of emails, a set of design screens.
For compound artifacts:
1. Run Step 0 (Intake) to map the components
2. Run Layer 1 at TWO levels: absences within individual components,
   AND absences in the relationships between components (what's not
   connected that should be? what's missing from the seams?)
3. Layers 2–4 often reveal more at the compound level than the component
   level — assumptions live in the gaps between parts

### What this skill cannot do
Be honest about the ceiling. Some findings require information that no
analytical framework can produce from the artifact alone:
- **Cross-repository emergence**: patterns forming across repos that no
  single-repo reviewer sees
- **Historical incident correlation**: this module causes outages when
  changed, but that requires incident database access
- **Organizational blindspots**: another team depends on this interface
  but there's no cross-team review process

The skill can *prompt the reviewer to go ask about* these things. It cannot
answer them from the artifact alone. When a finding depends on information
you don't have, say so explicitly: "This would be worth checking but I
can't verify it from what's available."

---

## Agent Mode: Pre-Commit Hook for Cognition

### What This Is

A compressed via-negativa pass designed to run at agentic decision points —
the moment an autonomous agent (coding agent, planning agent, debugging agent)
commits to a plan before executing it. The goal is not to review an artifact
someone made. It's to intercept the agent's own reasoning and surface what
it's blind to before it acts.

This is not reflection. Reflection asks "is my plan good?" and produces a
better version of the same plan. Agent mode asks "what is my plan blind to?"
and may reveal that the plan solves the wrong problem.

### Three intervention points

Agent mode operates at three distinct moments in an agentic loop:

**1. Pre-execution audit** — Before the agent acts on a plan.
**2. Loop-break diagnostic** — When the agent is stuck or looping.
**3. Task-framing challenge** — When the agent interprets a user's request
before starting work.

Each has its own protocol below.

---

### Intervention 1: Pre-Execution Audit

**When to trigger**: The agent has generated a plan (fix a bug, refactor a
module, implement a feature, choose an architecture) and is about to execute.

**Input**: The agent's reasoning trace and intended action.
- What does the agent believe is true?
- What does the agent intend to do?
- What is the agent's stated rationale?

**Protocol** (compressed Layer 1 + Layer 3, one pass):

1. **Assumption scan** (from Layer 2, compressed):
   List the 1–3 most load-bearing assumptions in the plan. For each:
   is it validated, plausible, or fragile? Focus only on assumptions that,
   if wrong, would make the entire plan fail — not just produce a suboptimal
   result.

2. **Absence scan** (from Layer 1, compressed):
   What is the plan not considering that is within its blast radius?
   Apply the Relevance Gate ruthlessly — only findings that are proximate,
   consequential, and non-obvious to the agent's own reasoning. Max 3 findings.

3. **Frame check** (from Layer 3, compressed):
   Is the agent solving the right problem? Does the plan's framing match
   the problem's actual shape? Specifically:
   - Is this a problem-solving plan when the real need is problem-understanding?
   - Is the agent optimizing when it should be exploring?
   - Is the agent treating a symptom as the root cause?
   - Is the plan shaped by the agent's capabilities rather than the problem's
     requirements? (hammer/nail)

   If the frame fits, say so and move on. Don't force a frame finding.

**Output format** (structured, for the agent loop to branch on):

```
## Pre-Execution Audit

**Proceed**: yes | yes-with-caveats | pause-and-reframe

**Blind spots** (max 3):
- [what the plan is not considering] → [concrete risk if unaddressed]

**Fragile assumptions** (max 2):
- [assumption] → [what breaks if wrong] → [how to validate before acting]

**Frame check**: [fit | mismatch]
- [If mismatch: what problem the agent is actually solving vs what problem
  needs solving. One sentence each.]

**Recommendation**: [proceed | address blind spots first | reframe the problem]
```

**Speed constraint**: This must complete in a single pass. No multi-layer
progressive disclosure. The value is in fast interception, not thorough
analysis. If a full stress test is warranted, the audit should recommend
pausing for one — not try to be one.

---

### Intervention 2: Loop-Break Diagnostic

**When to trigger**: The agent has attempted the same class of action 2+
times, is generating similar plans repeatedly, or is oscillating between
approaches without converging.

**Input**: The agent's recent action history — what it tried, what failed,
what it tried next.

**Protocol** (diagnostic mode, compressed):

1. **Pattern recognition**: What is the agent repeating? Name the loop.
   Not "it tried three times" but "it's applying fix-the-symptom strategies
   to a structural problem" or "it's searching for the bug in the wrong
   layer of the stack."

2. **Frame diagnosis** (Layer 3, diagnostic lens):
   Why is the agent stuck? The answer is almost never "it needs to try
   harder." Common loop causes:
   - **Frame lock**: The agent is debugging in Layer X when the bug is in
     Layer Y. It keeps generating Layer X solutions because its frame
     excludes Layer Y.
   - **False unity**: The agent is treating two different problems as one.
     Each attempt partially addresses one problem, which makes the other
     worse.
   - **Avoidance**: The agent's planning frame has no concept of
     abandonment. It cannot conclude "this approach fundamentally won't
     work" so it keeps iterating on a dead path.
   - **Optimization vs. exploration**: The agent is refining within a
     solution space when it should be searching across solution spaces.

3. **Escape vector**: Based on the diagnosis, what should the agent do
   differently? Not "try again" but a specific reframe — a different
   layer to investigate, a different decomposition of the problem, or
   an explicit recommendation to abandon the current approach.

**Output format**:

```
## Loop-Break Diagnostic

**Loop pattern**: [what the agent is repeating, named specifically]

**Why it's stuck**: [frame diagnosis — one of: frame-lock, false-unity,
avoidance, optimization-vs-exploration, or a novel diagnosis]

**The agent's current frame**: [what the agent thinks the problem is]
**What the frame excludes**: [what the agent cannot see from this frame]

**Escape vector**: [specific reframe or alternative approach]
**What to stop doing**: [the specific action pattern to abandon]
```

---

### Intervention 3: Task-Framing Challenge

**When to trigger**: A user gives the agent a task — "refactor this to
microservices," "build an auth system," "plan this migration" — and the
agent is about to interpret and execute.

**Input**: The user's request and the agent's initial interpretation of it.

**Protocol**:

This is not about asking the user clarifying questions about what they
want. Standard agents already do that. This is about surfacing what the
user is not thinking about — assumptions buried in their request that,
if surfaced, might change the request itself.

1. **Inherited assumptions in the request**: What is the user taking for
   granted that they might not have examined?
   - "Refactor to microservices" assumes microservices are the right
     architecture. Is the pain point actually coupling, and are there
     simpler decoupling strategies?
   - "Build an auth system" assumes auth needs to be built, not bought
     or delegated.
   - "Zero-downtime migration" assumes zero downtime is non-negotiable.
     Is it, or is that inherited from a context that no longer applies?

2. **The question behind the question**: What problem is the user
   actually trying to solve? The stated task is often a solution they've
   already chosen. What's the problem that led them to choose it, and
   does that problem have other solutions they haven't considered?

3. **Scope blindspots**: What will the user encounter during execution
   that they haven't anticipated? Not "you forgot to mention logging"
   but "this migration will require a data backfill strategy, and the
   approach you choose for that will constrain your rollback options
   in ways you should decide upfront, not discover mid-migration."

**Output format**:

```
## Task-Framing Challenge

**Inherited assumptions in this request** (max 3):
- [assumption the user is making] → [why it's worth examining]

**The problem behind the request**:
[What problem the user is actually solving. One sentence.]
[Whether the stated task is the only/best path to solving it. One sentence.]

**What you'll encounter that you haven't planned for** (max 2):
- [specific thing] → [why it matters to decide now rather than discover later]
```

**Critical constraint**: This intervention must be respectful of user
agency. The user may have already considered everything you surface.
Present findings as "worth confirming" not "you didn't think of this."
The goal is to make the user's implicit reasoning explicit so they can
confirm or revise — not to second-guess their competence.

---

### Agent Mode Anti-Patterns

These are the failure modes specific to agent mode. The general
anti-patterns in `references/anti-patterns.md` also apply.

**1. The Rubber-Stamp Audit**
Running a pre-execution audit that always says "proceed." If the audit
never catches anything, it's not filtering hard enough on frame check,
or the threshold for "pause-and-reframe" is too high. An audit that
always passes is security theater.

**2. The Overthinking Stall**
Running a pre-execution audit on trivial actions (renaming a variable,
adding a log line, fixing a typo). Agent mode should only trigger at
*consequential* decision points — plan commits, architecture choices,
debugging direction changes. Don't audit every action; audit commitments.

**3. The Reflection Disguise**
Producing output that's actually reflection ("let me verify my plan is
correct") dressed up as via negativa. The test: does the output surface
something the agent wasn't already considering? If it just validates or
iterates on the existing plan, it's reflection, not via negativa.

**4. The Infinite Regress**
Running via negativa on the via negativa output. "But what if my audit
missed something?" leads to audit loops. One pass. If the audit
recommends a reframe, execute the reframe and re-audit once. Never
more than two passes.

**5. The Condescending Challenge**
Task-framing challenges that second-guess competent, well-considered
user requests. "You said microservices, but have you considered a
monolith?" when the user has 50 services already and knows exactly
what they want. Apply the non-obvious criterion from the Relevance
Gate — if the user clearly already knows, don't surface it.

---

### Integrating Agent Mode into an Agentic System

Agent mode is designed to be inserted into existing agentic loops, not
to replace them. The integration point is the decision boundary — the
moment between "the agent has decided what to do" and "the agent does it."

**Minimal integration** (start here):
Insert a pre-execution audit at one decision point — the moment the
agent commits to a plan. Use Layer 1+3 compressed. Measure: how often
does the audit surface something that would have caused a failure or
wasted iteration? If the hit rate is > 15%, expand. If it's noise,
tune the Relevance Gate for machine-generated reasoning (which tends
to be more internally consistent but more frame-locked than human
reasoning).

**Loop-break integration** (add second):
Monitor the agent's action history. When 2+ similar actions have
failed, trigger a loop-break diagnostic instead of a retry. Measure:
does the agent escape the loop faster with diagnosis than with
retry-with-variation?

**Full integration**:
All three interventions active. Pre-execution audit on plan commits,
loop-break diagnostic on detected loops, task-framing challenge on
initial user requests. The system should have a bypass for trivial
actions (the Overthinking Stall anti-pattern).

---

## Quick Reference

For deeper examples and domain-specific templates, see:
- `references/anti-patterns.md` — **Read this first.** What bad via negativa output looks like — the performative critique, the obvious finding in fancy clothes, the forced Layer 3. Calibrate against these before producing output.
- `references/domain-checklists.md` — Absence checklists for 10+ artifact types (code, git, UI, data, infra, email, strategy, writing, processes)
- `references/code-review-examples.md` — Worked examples for PRs and code (prophetic mode)
- `references/strategy-examples.md` — Worked examples for business/strategy artifacts (prophetic mode)
- `references/debugging-examples.md` — Worked examples for bugs and incidents (diagnostic mode)
- `references/agent-mode-examples.md` — Worked examples for agent integration (pre-execution audit, loop-break, task-framing)
