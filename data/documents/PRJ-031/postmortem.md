# Post-Mortem: AI Governance & Responsible AI Program
**Date:** October 2024
**Status at close:** Completed 53 days behind the original plan; actual
cost $2.16M against a $1.60M budget (~35% over)

## What Happened
The governance framework was ultimately delivered and approved by
Trustline's board, but the schedule and budget overrun traces to a
single root cause identified in November 2023: the proposal assumed a
company-wide governance framework's regulatory review would be roughly
comparable in scope to the single-model compliance review completed for
Claims Fraud Detection. It was not — a company-wide, board-level
framework required documented risk classification for every current and
future AI use case, a substantially larger scope.

## Root Cause
This is the same underlying failure mode seen on the Meridian chatbot
engagement (PRJ-003): assuming a new AI governance scope is comparable to
a previously-completed, but narrower, compliance review on the same
account. Here it manifested at the framework level (company-wide
governance vs. single-model review) rather than the AI-output-type level
(generated text vs. risk scores), but the structural lesson is
identical.

## What Worked
Once the scope gap was identified and escalated with external regulatory
counsel involved directly, the extended review proceeded without further
surprises — the remaining schedule slip was contained to the one
identified gap, not compounded by additional discoveries.

## Lessons Learned
This is now the second engagement (see also PRJ-003) where "we've done
compliance work for this account before" was treated as informative
about a *new* compliance scope without verifying the two scopes are
actually comparable. Recommend this become a named, standing checklist
item across all regulated-industry proposals, not just addressed
reactively each time it recurs.
