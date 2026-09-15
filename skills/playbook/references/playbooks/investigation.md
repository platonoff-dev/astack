### Investigation

**You own the answer. Plan, route, write.**

Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change.

1. Load and follow the [how](../../../how/SKILL.md) skill over the subsystem in question. For motivation questions ("why was this built this way"), also load and follow the [why](../../../why/SKILL.md) skill.
2. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only investigation`.
3. Produce the `how`-shaped output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas), or a recommendation with a tradeoffs table if the request is a decision between alternatives.
4. Apply the [unslop](../../../unslop/SKILL.md) skill to the reply.

No delivery step, and no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature.

When delegation is available, `how` and `why` run as parallel workers per the Delegation paragraph in `SKILL.md`. Otherwise run them in sequence in the parent.

**Reply:** the investigation output. For "are we sure?" answers, include your real judgment with reasons. Push back if the premise is wrong; agreement is not the default.
