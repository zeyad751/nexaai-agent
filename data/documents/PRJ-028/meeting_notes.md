# Meeting Notes: SCADA Cloud Migration — Operations Escalation
**Date:** February 20, 2024
**Attendees:** Hanan Sabry (NexaAI PM), Sherif Shawky (NexaAI, Cloud),
Sahara Power Group CTO, Sahara Power Plant Operations Director

## Discussion
The Plant Operations Director opened with visible frustration: plant
engineering staff had effectively stalled cooperation with the migration
team, refusing to schedule the data-stream cutover windows the plan
required. Sherif Shawky noted this was a sharp contrast to the grid
analytics engagement, where IT-led change management had worked
smoothly.

The Plant Operations Director explained the distinction plainly: grid
analytics touched a reporting layer built on top of operational data —
plant engineers were largely unaffected day-to-day. SCADA systems are
the live control layer for physical grid equipment; plant engineers view
any change to it, however well-tested, as a direct safety and
reliability responsibility that sits with plant operations, not
corporate IT. The IT-led migration approach, effective for the analytics
platform, was read by plant engineering as corporate IT overstepping
into operational-safety territory without operations' own sign-off
authority built into the process.

The Group CTO acknowledged that the proposal's assumption — that the
prior engagement's IT-led methodology would transfer — had not accounted
for this IT/OT (information technology / operational technology)
distinction.

## Decision (Strategy Pivot — Negative outcome for the original approach)
The team agreed the IT-led migration approach, as originally scoped, was
not viable given plant operations' authority over live control systems.
Logged as a negative-outcome decision for the original plan.

## Revised Direction
The team pivoted to an OT-embedded migration approach: plant operations
engineers formally co-own each cutover decision, with NexaAI providing
technical execution but operations holding sign-off authority at every
migration stage — slower per-stage, but structurally addressing the
authority concern rather than trying to persuade around it.

## Action Items
- NexaAI to redesign the migration governance model with formal OT
  sign-off gates at each stage
- Sahara Power Plant Operations to name dedicated engineering
  co-owners for the remaining migration phases
