# Tracker adapter

Keep intake independent of Jira, GitHub Issues, Linear, or local files. Use the
project's existing tracker instructions, often `docs/agents/issue-tracker.md`.
Do not infer its tracker from where the Git remote is hosted. If no mapping
exists, use supplied text or an accessible URL and save a local draft. Ask which
tracker to use only when access or publication requires that decision.

An adapter can be a short project document mapping these operations to available
MCP tools, CLI commands, or APIs. Do not scaffold a server, install an integration,
or add other tracker implementations during intake. Do not store credentials in
the document. Read the provider's current tool schema or documentation when an
operation or format is unknown.

| Operation | Contract |
|---|---|
| Read task | Identity and URL/path, description, current discussion, dates/revision, attachment references, relationships; disclose missing or inaccessible content |
| Search related work | Query by relevant concepts, signatures, triggers, versions, and source link; report what was searched and distinguish duplicates from possible relations |
| Read brief | Locate the identified intake brief, its ID/path and current revision; if competing versions cannot be reconciled, surface the conflict |
| Publish brief | Create or update that brief, preserve unrelated content and human edits, return a stable reference, and verify it by reading back |

Record the project/destination, available operations, how the brief is located,
format conversion, and any existing publication authorization. Missing search
or write capability limits the result; it must not masquerade as "no duplicate"
or "published". Access to private evidence is not permission to republish it.

## Local Markdown adapter

Read the supplied task file and any referenced local discussion. Search the
configured task directory if one exists; otherwise disclose that tracker-wide
deduplication was unavailable. Keep one `brief.md` in the task workspace. Its
absolute path is the handoff reference and remains authoritative for local-only
work. Writing this draft does not create remote issues or change task status.

## Remote publication

1. Finish the local draft and resolve blockers for its chosen next action. A
   brief that asks for a decision may be published as such, never as ready to
   implement. Honor existing authorization; otherwise present the exact draft
   and request publication permission. Do not ask again for an action already
   authorized in this session or by project policy.
2. Reread the source and existing brief. Reconcile new discussion or human edits
   before writing. Use a conditional update when the provider supports one;
   otherwise reread immediately before writing and disclose unresolved conflicts.
3. Publish a clearly identified "Task intake brief" comment or existing agreed
   location. Preserve the original ticket description by default. Store its
   returned ID/permalink and source revision with the local working copy.
4. Update that identified brief on later runs. After an ambiguous write result,
   inspect the destination before retrying so a timeout does not create duplicate
   comments. If updates are unsupported, publish a revision explicitly linking
   the version it supersedes, only when that write is authorized.
5. Read back and confirm the content and reference. Never report publication
   merely because a write was attempted. Keep a usable local draft on failure.

Translate Markdown into the provider's supported comment format. Ensure shared
evidence links are accessible to the intended audience; local absolute paths are
not shared links. Preserve source visibility and redact sensitive material.
After publication, the tracker version is authoritative and local edits are new
drafts until published. There is no automatic background synchronization.

Publication does not authorize creating child tickets, assigning owners, changing
priority/status, closing issues, or posting questions to other people. Those are
separate actions requiring their own existing or explicit authorization.
