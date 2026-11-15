# Meeting Notes: Chatbot Project — Legal & Compliance Escalation
**Date:** June 18, 2024
**Attendees:** Hady Adeyemi (NexaAI PM), Tarek Nabil (NexaAI, Strategy),
Meridian Legal & Compliance team, Meridian Head of Customer Experience

## Discussion
Meridian's Legal & Compliance team, reviewing sample chatbot transcripts
from internal testing, flagged that several generated responses to
transaction-dispute questions came close to characterizing outcomes in
ways that could be read as financial guidance — a regulatory line the
bank is required to stay well clear of for any customer-facing channel,
automated or not.

Tarek Nabil noted that this had not been scoped as a distinct review
track in the original proposal — the assumption going in was that this
engagement's compliance profile would resemble the Fraud Detection
project's, which deals with internal risk-scoring rather than
customer-facing generated language. Legal clarified that customer-facing
generated text is subject to a different, and in some ways stricter,
review process than internal model outputs, since it is the bank's
literal "voice" to the customer.

The Head of Customer Experience expressed frustration at the prospect of
delaying the Q3 pilot, noting this project had been positioned internally
as the flagship deliverable of the broader AI transformation roadmap and
a visible delay would be noticed at the executive level.

## Decision
The team agreed to insert a formal compliance review gate before any
further customer-facing testing proceeds, with NexaAI's Cybersecurity/
Responsible AI team engaged to design response-guardrail testing
specifically for financial-advice-adjacent language. This was logged as
a mixed-outcome decision: necessary and correct, but a real cost to the
original schedule.

## Action Items
- NexaAI Cybersecurity team to design a guardrail test suite for
  financial-advice-adjacent language by early Q3
- Meridian Legal to provide example language patterns considered
  out-of-bounds, to seed the test suite
