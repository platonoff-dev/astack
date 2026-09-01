# Reserved playbook routes

Task intake records one route in `Playbook`. The files exist so each route can
be researched and adopted separately. They remain intentionally empty in
version 0.8.0. A route name does not yet define a procedure, entry condition,
completion check, or transition.

| Playbook | Status |
|---|---|
| `investigation` | placeholder |
| `bug-fix` | placeholder |
| `feature` | placeholder |
| `refactor` | placeholder |
| `performance` | placeholder |
| `migration` | placeholder |
| `decision` | placeholder |
| `split` | placeholder |
| `no-change` | placeholder |

Choose the name that best describes the task's current job. Record uncertainty
instead of pretending the empty playbook settles classification. `Modifiers` may
name a secondary concern, but no modifier has adopted behavior yet.

Do not derive detailed rules from the route's English name or from external
playbooks. Every playbook needs its own prior-art review, decision record,
instructions, and behavioral trial. When one is adopted, update its file, the
adopted set in `main/scripts/check_playbooks.py`, this status table, and
the plugin version in the same change.
