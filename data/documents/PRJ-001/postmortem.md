# Post-Mortem: Fraud Detection AI Platform
**Date:** February 2024
**Status at close:** Completed on schedule (planned end 2024-02-12, actual
2024-02-13), actual cost slightly under budget ($1.57M vs. $1.62M budget)

## What Happened
The platform was delivered in four phases as planned, with the digital
banking pilot extended by one quarter (see Feb 2023 steering committee
decision) to build a stronger production track record ahead of the
higher-volume retail rollout. That extension proved worthwhile: the
retail-channel model risk committee review in late 2023 was the fastest
of the three channel reviews, explicitly citing the digital-channel
track record as a factor.

## What Worked
- The Responsible AI Framework's built-in governance checkpoints, while
  adding process overhead, meant no release was ever delayed by a
  governance finding raised late — every finding surfaced during the
  scheduled review windows.
- Analyst adoption, which started slowly, climbed steadily once the
  risk-score explanations started being used directly in case
  documentation — a benefit that emerged organically rather than being
  part of the original scope.
- Cross-functional staffing (AI Engineering, Data & Analytics,
  Cybersecurity, and Finance all represented from kickoff) meant
  compliance and financial questions were answered within the team
  rather than becoming external dependencies.

## A Note on the ROI Trend
Reported ROI looks unusual at first glance — very high in the first two
quarters (digital-channel pilot, low cumulative cost, early wins) and
then declining as the platform scaled to retail and mobile channels
(higher cumulative investment). This is not a performance regression: it
reflects a small, cheap pilot generating an outsized early ratio before
the full-scale investment caught up. By project close, ROI had settled at
a still-strong ~46% against the full three-channel investment, alongside
adoption climbing to over 90% and customer satisfaction from the fraud
operations team at 8.8/10 — the more representative steady-state picture.

## Lessons Learned
- Building in a deliberate "extend the pilot" checkpoint before scaling
  to a higher-stakes channel was more valuable than the original plan
  assumed — worth proposing as a standard pattern for future regulated
  fraud/risk engagements.
- Early ROI figures on a phased rollout should be presented to clients
  with explicit framing about scale, to avoid setting an anchor that
  later, more representative figures will appear to undershoot.
