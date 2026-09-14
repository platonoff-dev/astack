# Fix Root Causes

When debugging, do not fix symptoms. Trace every problem to its root cause and fix it there.

**Why:** Symptom fixes accumulate. Each workaround makes the system harder to reason about, and the real bug remains. Root-cause fixes are slower upfront but reduce total debugging time.

**Pattern:**
- Reproduce first
- Ask "why" until you hit the root cause
- Do not add guards merely to hide a broken invariant or silence a crash. Keep validation at trust boundaries and guards that implement valid domain behavior; fix the cause of invalid internal state.
- If a workaround needs a paragraph-long comment to justify it, the code is wrong (fix the code, not the comment)
- Check for the pattern, not just the instance (search for the same pattern, fix confirmed instances within the authorized task scope, and report related instances outside that scope).
- When stuck, instrument. Don't guess (add logging, read the actual error)

**Restart bugs: suspect state before code**

When something "fails after restart," suspect stale persistent state first: config files, caches, lock files, serialized state. If clearing a state file restores behavior, prioritize state validation as the fix.
