# Meeting Notes: Claims Fraud Detection — Investigator Feedback Review
**Date:** October 20, 2022
**Attendees:** Aya Fahmy (NexaAI PM), Ryan Al-Otaibi (NexaAI, AI
Engineering), Trustline Head of Claims Investigation, three senior
claims investigators

## Discussion
Ryan Al-Otaibi opened with strong model performance metrics: fraud
detection precision and financial-loss-avoidance figures were both
tracking well ahead of the original business case. The mood in the room
did not match the numbers, however — the three investigators present
were candid that they found the new scoring workflow frustrating to work
with, not because it under-performed technically, but because the
model's score explanations were framed in statistical terms (feature
contribution weights) that did not map onto how investigators actually
build a fraud case narrative for their own review documentation. Several
investigators reported spending extra time translating model output into
their own case-notes format, which felt to them like added work rather
than the promised triage-time reduction.

The Head of Claims Investigation acknowledged the financial case for the
model was clearly strong and that Trustline had no intention of rolling
it back, but agreed the investigator experience had not been prioritized
during design in the way the fraud-detection accuracy had been.

Aya Fahmy offered additional training sessions on interpreting model
output, which the investigators accepted, though without much
enthusiasm — one investigator noted training would help them cope with
the interface, not fix that the interface wasn't built around how they
actually work.

## Decision
The team agreed to offer supplementary training as a near-term measure.
No redesign of the scoring interface was committed to, given the
strength of the financial case and the remaining budget/timeline — the
client explicitly chose to accept the solution as-is rather than fund
an interface redesign.

## Action Items
- NexaAI to deliver two additional training sessions on interpreting
  model score explanations
- Trustline to continue monitoring investigator sentiment informally;
  no further action committed at this time
