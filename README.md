# Via Negativa Stress Test

A metacognitive skill that equips an LLM with negative perception — the ability to see what's **absent, assumed, and structurally excluded** from any artifact or system.

Most review asks *"is what's here correct?"*
Most debugging asks *"where is the error?"*
This asks *"what's NOT here, and does its absence matter?"*

## Three Modes

**Prophetic** (review / stress test): Nothing is broken yet. What's absent that will become the failure? What's invisible that would change the decision if seen?

**Diagnostic** (debugging / root cause): Something is broken. What structural absence made this class of failure inevitable? What's missing from the system that would make this bug impossible?

**Agent** (cognitive proprioception): An autonomous agent is reasoning toward action. What is that reasoning blind to? Is the agent solving the wrong problem?

## Quick Start

### As a Claude Skill

Drop `SKILL.md` and `references/` into your Claude project or skill directory. Then:

```
# Prophetic mode
stress test this PR
poke holes in this architecture doc
what am I not seeing in this business plan?

# Diagnostic mode
why does this test keep flaking?
what's really going on with this memory leak?
this bug doesn't make sense — what am I missing?
```

### Agent Mode

Agent mode runs at decision points inside agentic loops — not on artifacts a human hands it, but on the agent's own reasoning before it acts. There are three intervention points:

#### 1. Pre-Execution Audit

Insert at the moment an agent commits to a plan. The audit runs a compressed Layer 1+3 pass on the agent's reasoning and outputs a structured verdict: `proceed`, `yes-with-caveats`, or `pause-and-reframe`.

**To use in a system prompt or agent wrapper:**

```
Before executing your plan, run a via-negativa pre-execution audit:
1. What are the 1-2 most fragile assumptions in your plan? What breaks if they're wrong?
2. What is your plan not considering that's within its blast radius? (max 3 findings)
3. Frame check: are you solving the right problem, or are you solving the problem
   your tools/frame make easy to solve?

Output your audit as:
- Proceed: yes | yes-with-caveats | pause-and-reframe
- Blind spots (max 3)
- Fragile assumptions (max 2)
- Frame check: fit or mismatch
- Recommendation
```

**When to trigger**: Consequential decisions only — plan commits, architecture choices, debugging direction changes. Not every action. Renaming a variable doesn't need an audit; deciding to refactor a module does.

#### 2. Loop-Break Diagnostic

Insert when the agent has attempted the same class of action 2+ times without success. Instead of retrying with variation, diagnose *why* the agent is stuck.

**To use in a system prompt or agent wrapper:**

```
You've attempted similar approaches multiple times without success. Before trying again,
run a via-negativa loop-break diagnostic:
1. Name the loop: what pattern are you repeating?
2. Why are you stuck? Common causes:
   - Frame lock: debugging in the wrong layer/abstraction
   - False unity: treating two different problems as one
   - Avoidance: unable to conclude "this approach won't work"
   - Optimization vs exploration: refining one solution when you should search across solutions
3. What should you do differently? Not "try harder" — a specific reframe.
4. What should you stop doing?
```

**When to trigger**: After 2+ failed attempts at the same class of solution. The signal is not "it failed twice" but "the agent's approach hasn't fundamentally changed between attempts."

#### 3. Task-Framing Challenge

Insert when the agent interprets a user's request, before starting execution. Surfaces assumptions buried in the request that might change the request itself.

**To use in a system prompt or agent wrapper:**

```
Before starting this task, run a via-negativa task-framing challenge:
1. What assumptions are inherited in the user's request that they may not have examined?
   (max 3)
2. What problem is the user actually solving? Is the stated task the only/best path?
3. What will the user encounter during execution that they haven't anticipated? (max 2)

Present findings as "worth confirming" — respect user agency.
```

**When to trigger**: Complex or ambiguous tasks. Not "add a log line" but "refactor to microservices" or "plan this migration." Tasks where the framing choice has as much impact as the execution quality.

#### Integration Strategy

**Start small**: Pick one intervention point — pre-execution audit is highest leverage. Insert it at the moment the agent commits to a plan. Measure how often the audit surfaces something that would have caused a failure or wasted iteration. If the hit rate is meaningful (>15%), expand to loop-break and task-framing.

**Avoid audit fatigue**: Only trigger on consequential decisions. If the audit runs on every action, the agent (or user) will learn to ignore it. The Relevance Gate exists for this reason — fewer, higher-signal findings beat comprehensive coverage.

**One pass only**: Agent mode is designed for speed. One pass, structured output, done. If the audit recommends a reframe, execute the reframe and re-audit once. Never more than two passes. See the "Infinite Regress" anti-pattern.

### Investigation Scripts (for PRs and code)

```bash
./scripts/run-all.sh --base main              # full investigation
./scripts/blast-radius.sh --base main         # blast-radius only
./scripts/co-change-gaps.sh --base main       # co-change only
```

**Requirements**: bash, git, grep, bc. No external dependencies.

## Scripts

| Script | Answers |
|--------|---------|
| `blast-radius.sh` | Who is affected by this change that the diff doesn't show? (import-aware) |
| `co-change-gaps.sh` | What files usually change alongside this but weren't changed? |
| `churn-report.sh` | Is this a fragile area that keeps getting patched? |
| `abandoned-approaches.sh` | What did previous engineers try and abandon here? |
| `trajectory.sh` | Is this the Nth PR adding complexity without refactoring? |
| `run-all.sh` | Run all of the above. |

## The Skill

Four-layer progressive analysis: **Absence Inventory** → **Load-Bearing Assumptions** → **Frame Exclusions** → **Via Negativa Design**. Default depth is all four layers — Layers 3–4 are where the differentiating insight lives. Layer 3 reveals what the creator's frame made impossible to see; Layer 3b (stochastic perturbation) extends this by sampling from the complement of the known predicate space through parallel sub-agents, surfacing emergent predicates that analytical frame analysis cannot reach. Layer 4 synthesizes the negative space into what the artifact is actually reaching toward.

Agent mode adds a compressed Layer 1+3 protocol for agentic decision points — see the Agent Mode section in `SKILL.md` for full methodology.

See `SKILL.md` for full methodology.

## What Makes This Different From Reflection

Every agent framework has some version of "reflect on your output." The difference is structural:

- **Reflection** asks: "Is this good?" → produces validation or iteration
- **Via negativa** asks: "What is this blind to?" → produces revelation

Reflection improves answers. Via negativa changes the question. An agent that reflects will produce a better version of the same plan. An agent that runs via negativa might realize it's solving the wrong problem.

## References

| File | Purpose |
|------|---------|
| `references/anti-patterns.md` | What bad output looks like — calibrate against these before producing findings |
| `references/agent-mode-examples.md` | Worked examples for agent integration (pre-execution audit, loop-break, task-framing) |
| `references/code-review-examples.md` | Worked examples for PRs and code (prophetic mode) |
| `references/strategy-examples.md` | Worked examples for business/strategy artifacts (prophetic mode) |
| `references/debugging-examples.md` | Worked examples for bugs and incidents (diagnostic mode) |
| `references/domain-checklists.md` | Absence checklists for 10+ artifact types |

## License

MIT
