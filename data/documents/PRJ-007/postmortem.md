# Post-Mortem: Back-Office Claims Automation
**Date:** December 2023
**Status at close:** Completed 43 days behind the original plan; actual
cost $410.6K against a $313.6K budget (~31% over)

## What Happened
The automation was delivered and is in production, but the schedule and
budget overrun trace to a single recurring theme: certain claim
categories that looked purely administrative during scoping turned out,
on closer compliance review, to sit closer to clinical judgment than the
original "administrative vs. clinical" boundary assumed. The
prescription-quantity case (see July 2023 meeting notes) was the clearest
example, but two smaller claim categories required similar mid-project
re-scoping into human-review queues rather than full automation.

## Root Cause
Automation-First is a strong strategy for genuinely administrative,
high-volume back-office work, and NexaAI has strong results applying it
in Manufacturing and Logistics accounts. In a healthcare claims context,
however, "administrative" and "requires clinical judgment" are not always
cleanly separable at the individual-claim-category level — several
categories that appeared administrative in aggregate contained edge cases
that were not.

## What Worked
Once each boundary case was identified, the escalation-queue pattern
established at kickoff made it straightforward to redirect that category
to human review without redesigning the broader automation architecture.
No category required scrapping automated work already built.

## Lessons Learned
For any Automation-First engagement in a healthcare or clinical-adjacent
context, budget explicit time during claim-category design for a
compliance-officer review of each category — not just an operations-team
review — before committing automation scope and schedule. Operations and
compliance apply different criteria for what counts as "routine."
