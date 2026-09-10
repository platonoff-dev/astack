# Product Analytics and Warehouse Evidence

## What this source contains

A warehouse can hold product events, usage or billing records, experiment
exposures, feature-flag outcomes, pipeline lineage, and query telemetry. These
complement infrastructure logs and errors: they can show what users experienced
and what data was available when a decision was made.

Databricks is one example provider. Use the actual available warehouse interface
and SQL dialect. No analytics table, event name, timestamp column, dbt model,
deduplication rule, or refresh schedule is assumed by this playbook.

## How to search it

1. **Inspect the interface.** Find schema inspection and read-only query operations
   in the available connector, API, or CLI. Check whether queries are asynchronous;
   poll a returned statement/job identifier through the supported read operation
   rather than resubmitting. Do not run writes, DDL, refreshes, notebooks, or remote
   analysis jobs. If read-only query execution is unavailable, report the gap.
2. **Discover the schema.** Use catalog metadata, table descriptions, or the
   provider's equivalent of `SHOW TABLES` / `DESCRIBE TABLE`. Find relevant event,
   experiment, or usage tables and verify their actual columns. Use source access
   guides when supplied, but verify that their schemas still match this workspace.
3. **Understand the data contract.** Determine timestamp semantics and timezone,
   partition columns, row grain, identifiers, duplicates, sampling, refresh lag,
   retention, and relevant schema changes. Prefer documented curated models only
   when their definitions support the question. Do not assume every dbt model is
   deduplicated or has a particular physical layout.
4. **Bound the query.** Select a window around the actual deployment or event date
   when known; a merge date is only a proxy. A few weeks on either side can be a
   starting point, adjusted to the question and available retention. Filter using
   verified time and partition columns; aggregate and limit output. Avoid an
   unbounded raw-event scan.
5. **Inspect definitions and lineage when available.** A curated model's SQL or
   documented lineage can explain transformations and dependencies. Return code
   history leads to the source-control investigator. Do not assume a SQL connector
   can retrieve notebooks or other documents; record unsupported content as a gap.

An illustrative query shape, with every identifier resolved from metadata and
syntax adapted to the actual dialect:

```sql
SELECT <day_bucket>, COUNT(*) AS event_count
FROM <verified_table>
WHERE <verified_timestamp> >= <window_start>
  AND <verified_timestamp> < <window_end>
  AND <verified_event_filter>
GROUP BY <day_bucket>;
```

## Useful investigation patterns

- **Usage trajectory:** counts around a feature's deployment, noting sampling and
  instrumentation changes before interpreting a rise as adoption or a decline
  as removal.
- **Threshold origin:** pre-change distributions of a verified measurement,
  compared with the code's constant. A matching percentile is circumstantial
  evidence; it does not prove how the author chose the value.
- **Experiment or flag history:** verified exposures, outcomes, and any documented
  rollout decision. Exposure alone is not proof that a variant shipped.
- **Query or pipeline pressure:** supported query-history metadata can reveal
  expensive operations around a migration or optimization. Discover available
  metadata tables and fields; do not assume access to system telemetry.
- **Defensive-code effects:** compare relevant errors before and after deployment,
  controlling for event-definition changes and other releases where possible.

## Common pitfalls

Correlation does not establish authorship or intent. Match numeric findings to
commits, review discussions, or decision records before claiming a causal rationale.
Zero rows can mean missing retention, refresh lag, permissions, changed schemas,
or a bad filter; distinguish those from a verified absence of activity. Do not
silently combine different event definitions across time.

## What to return

For each finding, provide the source/table, exact query, time window and timezone,
data grain and known quality limits, a compact numeric summary, correlation with
the target's deployment (or the date proxy used), and evidence strength. Do not
dump raw user records. State remaining schema, access, and retention gaps.
