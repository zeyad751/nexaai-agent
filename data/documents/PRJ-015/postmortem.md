# Post-Mortem: Data Platform Modernization
**Date:** June 2024
**Status at close:** Completed 43 days behind the (already-revised)
plan; actual cost $2.74M against a $2.17M budget (~26% over)

## What Happened
This engagement never fully recovered the schedule and budget position
lost to the April 2023 discovery-phase finding: Delta Steel's enterprise
systems (ERP, procurement) were significantly less mature than the
proposal assumed, based on generalizing from the unrelated success of
the 2022 Predictive Maintenance engagement's sensor-data pipeline.

## Root Cause
This is the same failure mode as the proposal-stage risk noted explicitly
at the time: **data maturity does not transfer across unrelated domains
within the same client.** A client can have excellent, modern
instrumentation on one system (plant-floor sensors, in this case) and a
15-year-old, poorly documented system elsewhere (enterprise ERP). The
2022 engagement's success created organizational confidence that, in
hindsight, did not warrant skipping a proper systems-level data maturity
assessment for this specific, different set of source systems.

## Contrast Worth Noting
NexaAI ran the same Data-First Transformation strategy on the Falcon
Gulf Bank credit risk engagement (PRJ-004) around the same period, where
a genuine systems-level maturity assessment was conducted upfront and the
engagement succeeded cleanly. The strategy itself is not the problem —
skipping or shortcutting the maturity assessment is.

## What Worked
Once the expanded remediation scope was agreed, the team's execution of
that expanded work was solid — ROI trended from deeply negative (-28.9%)
toward breakeven by close, and adoption climbed steadily (19.6% to 41.6%)
even through the rocky middle of the engagement, suggesting the
eventual platform quality was reasonable once properly remediated.

## Lessons Learned
Prior engagement success with a client should never substitute for a
systems-level data maturity assessment on a *new* set of source systems,
even when both engagements are with the same client and even when the
same overarching strategy worked well before. Maturity is a property of
the specific systems in scope, not of the client relationship as a whole.
