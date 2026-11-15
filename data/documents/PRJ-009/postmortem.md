# Post-Mortem: Enterprise Clinical AI Rollout
**Date:** January 2024
**Status at close:** Completed, 30 days behind the original plan; actual
cost $626.9K against a $559.1K budget (~12% over) — but revenue came in
well above plan at $911K, reflecting an expanded scope agreed after the
pivot

## What Happened
This project had a rocky first two months, followed by one of the
strongest recoveries on record for a NexaAI engagement. Early KPI
reporting (overall project score 38.7 in Q2 2023) reflected genuine
trouble: the original single-custom-model scale-up approach broke down
once network-wide documentation style diversity became apparent (see
April 2023 meeting notes). By project close, overall score had climbed to
67.0, with customer satisfaction rising from 4.1 to 7.8 and adoption from
12% to over 61%.

## Root Cause of the Early Struggle
The pilot's success created a false confidence in "generalization by
default" — the pilot department's unusually disciplined documentation
style was mistaken for a representative sample of network-wide practice.
This was a data quality risk that was identifiable in principle at
proposal stage (a note-style audit across departments would have surfaced
it) but was not caught until real training data exposed it.

## What Turned It Around
The pivot from a single trained model to a retrieval-augmented,
Product-Led AI approach was the turning point. This mattered for two
reasons beyond the immediate technical fix: it removed the need to
retrain a custom model per department's documentation style (prompt and
retrieval tuning is far cheaper to iterate than model retraining), and it
reframed the engagement around an internal Nileside owner continuing to
improve the capability after NexaAI's involvement ends — which is
structurally why Product-Led AI outperformed the original strategy here,
not just a one-time technical fix.

## Lessons Learned
A successful pilot's data characteristics should never be assumed
representative of network-wide or organization-wide data without an
explicit sampling check across the intended full-scale population — this
is a specific, checkable failure mode distinct from the more general
"client data maturity" question raised on other accounts.
