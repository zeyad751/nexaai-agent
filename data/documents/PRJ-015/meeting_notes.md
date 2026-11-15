# Meeting Notes: Data Platform Modernization — Discovery Findings Escalation
**Date:** April 20, 2023
**Attendees:** Karim Youssef (NexaAI PM), Ahmed Qureshi (NexaAI, Data &
Analytics), Tarek Nabil (NexaAI, Strategy), Delta Steel Group CIO, Delta
Steel Finance Director

## Discussion
Ahmed Qureshi presented findings from the three-week technical discovery
phase, and the tone in the room shifted quickly. Unlike the plant-floor
sensor systems from the 2022 engagement — modern, well-instrumented, and
centrally managed — the ERP and procurement systems in this engagement's
scope turned out to be a mix of a 15-year-old on-premise ERP
implementation with minimal data dictionary documentation, and a
procurement system maintained almost entirely through spreadsheet
exports with no consistent schema between plants.

The Finance Director pushed back initially, noting that Finance's own
reporting had "always worked fine" — Ahmed Qureshi clarified that the
issue was not whether existing reports worked for their narrow original
purpose, but whether the underlying data was structured and documented
well enough to support automated consolidation into a governed platform
without extensive manual remediation first.

Tarek Nabil noted directly that the proposal's assumption — that the
prior engagement's data maturity would extend to these systems — had
not held, and that continuing on the original 6-month foundation-build
timeline without addressing this would produce an unreliable platform.

## Decision
The team agreed to expand the data cleansing and governance workstream
substantially beyond the original scope, effectively adding a
remediation phase the original plan had not budgeted for. This was
logged as a negative-outcome decision: necessary, but a direct
consequence of a proposal-stage assumption that did not generalize from
the 2022 engagement to this one.

## Action Items
- NexaAI to produce a revised timeline and budget estimate reflecting the
  expanded remediation scope
- Delta Steel Finance and Procurement to assign dedicated data stewards
  for the remediation phase
