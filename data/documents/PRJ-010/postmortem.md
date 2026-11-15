# Post-Mortem: Personalized Recommendation Engine
**Date:** January 2023
**Status at close:** Completed on schedule; actual cost $689.6K against a
$655.2K budget (~5% over)

## What Happened
The recommendation engine launched successfully and customer-facing
metrics were strong throughout: satisfaction climbed from 7.4 to 8.5 and
adoption (share of sessions engaging with recommended products) grew from
roughly 31% to 63%. Financially, ROI held flat around 14% across the
engagement — solid but unremarkable, and clearly the weaker half of an
otherwise strong-looking project.

## Root Cause of the ROI/Satisfaction Gap
Two compounding factors, both traceable to the original proposal's
framing rather than a delivery failure:
1. The business case was built around engagement and satisfaction
   metrics from the outset (see proposal), not a specific
   revenue-attribution target — so there was no dedicated infrastructure
   to isolate and demonstrate incremental revenue cleanly, even though
   the qualitative signal (customer feedback, engagement lift) was
   strongly positive.
2. Additional tuning cycles for lower-traffic ("cold-start") product
   categories, flagged as a risk at kickoff, materialized as a real cost
   overrun that directly compressed the ROI figure without a
   corresponding revenue metric to offset it in reporting.

## What Worked
The core recommendation quality and customer reception were genuinely
strong — this is not a case of the technology underdelivering. The
satisfaction and adoption trends are the more representative measure of
what this project actually achieved for the customer experience.

## Lessons Learned
When a business case is framed primarily around engagement/satisfaction
rather than a hard revenue target, build a lightweight revenue-
attribution mechanism (even basic A/B holdout tracking) into the initial
scope regardless — otherwise a genuinely successful project can end up
looking financially unremarkable purely for lack of a way to measure its
financial upside, not because that upside doesn't exist.
