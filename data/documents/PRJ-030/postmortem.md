# Post-Mortem: Claims Fraud Detection
**Date:** January 2023
**Status at close:** Completed 10 days behind the original plan; actual
cost $516.3K against a $537.8K budget (under budget)

## What Happened
Financially, this was one of the strongest results in the portfolio —
ROI peaked at 136% in the first reporting period and settled at a still
excellent 69.5% by close, with revenue reaching $875K against a $516K
investment. Investigator satisfaction told a different story throughout:
starting at 4.2/10 and declining slightly to 3.6/10 by close, the
weakest satisfaction trend of any completed project in the portfolio.

## Root Cause
The original business case (see proposal) was built around
fraud-loss-reduction and efficiency metrics, with an explicit assumption
that investigator satisfaction would not be a significant factor. That
assumption did not hold: investigators found the model's statistical
explanation format mismatched with how they actually build case
narratives, creating a real, if not officially budgeted-for, cost in
daily workflow friction — separate from and invisible to the financial
metrics the business case tracked.

## What Worked
The underlying model quality was never in question — this is not a
technical failure. The financial case was strong enough that Trustline
explicitly chose to accept the interface friction rather than fund a
redesign, a reasonable business decision given the numbers, even though
it left a real, unresolved user experience gap.

## Lessons Learned
When a business case explicitly assumes a stakeholder group's experience
"will not be a significant factor," treat that as an assumption to
validate early (e.g., a short interface-usability check with actual
end users during design), not a premise to build the whole engagement
on unchallenged. A technically and financially excellent model can still
carry a real, un-costed friction tax on the people who have to use it
daily.
