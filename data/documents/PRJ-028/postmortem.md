# Post-Mortem: Cloud Migration for SCADA Data Systems
**Date:** July 2025
**Status at close:** Completed 34 days behind the original plan; actual
cost $2.21M against a $1.92M budget (~15% over) — but recovered strongly
after a difficult start (overall project score climbed from 34.8 to 63.1
across the engagement)

## What Happened
An early, sharp stall (see February 2024 meeting notes) when plant
operations engineering effectively refused to cooperate with the
originally-scoped IT-led migration approach, followed by a structural
pivot to an OT-embedded governance model that unblocked progress and
carried the project to a strong recovery.

## Root Cause
The proposal assumed the grid analytics engagement's successful IT-led
change-management approach would transfer directly to a SCADA migration.
This missed a specific and, in hindsight, obvious distinction: grid
analytics is a reporting layer atop operational data; SCADA is the live
control layer itself. Plant operations engineers hold — correctly —
safety and reliability authority over the latter that they do not hold
over the former, and no amount of IT-led persuasion was going to
substitute for giving operations formal sign-off authority in the
process itself.

## What Worked
Once the OT-embedded governance model was adopted, migration progress
resumed steadily. Notably, adoption dipped slightly in Q3 2024 (8.7%,
down from 10.6% the prior quarter) even as the new governance model was
being stood up — a short-term cost of the transition — before climbing
strongly to 68.1% by close as the new model took hold.

## Lessons Learned
For any Cloud-First AI or infrastructure migration engagement touching
live operational control systems (SCADA, industrial control systems,
or similar), do not assume a prior engagement's change-management
approach transfers, even for the same client, if the prior engagement
sat at a different layer (analytics/reporting vs. live control). Build
in operational sign-off authority structurally from the start for
anything touching live control systems.
