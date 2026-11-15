# Post-Mortem: AI-Powered Customer Service Chatbot
**Date:** May 2025
**Status at close:** Completed, ~54 days behind the original plan; actual
cost $2.32M against a $1.87M budget (~24% over)

## What Happened
The project delivered its full scope — an assistant covering the
target inquiry categories, integrated with the service ticketing system —
but with significant schedule slippage traced to a single root cause: the
compliance review requirements for customer-facing generated language
were materially underestimated at the proposal stage.

## Root Cause
The original proposal assumed this engagement's compliance profile would
resemble the Fraud Detection AI Platform's, since both fall under
Meridian's Responsible AI umbrella. In practice, Legal & Compliance
treats customer-facing generated text as a distinct and stricter review
category from internal risk-scoring outputs, because it is directly
attributable to the bank as its "voice" to the customer. This distinction
was not surfaced until internal testing in June 2024, roughly three
months into delivery, when transcripts revealed responses that came close
to constituting financial guidance.

## What Worked
- Once escalated, the response was fast: a dedicated guardrail test suite
  was designed and the compliance gate was cleared within one additional
  quarter, not multiple.
- The retrieval infrastructure itself performed well throughout — the
  delay was entirely on the language-guardrail side, not the underlying
  retrieval-and-generation architecture.

## What Could Have Gone Better
- A proposal-stage assumption ("this account's compliance profile is
  already understood from the Fraud project") went unchallenged despite
  covering a materially different type of AI output (generated
  customer-facing text vs. internal risk scores).
- Customer Experience leadership's expectation that this would be a fast
  flagship win created pressure that, in hindsight, the original schedule
  should not have set given the review requirements involved.

## Lessons Learned
For any new generative, customer-facing use case on an existing account,
do not assume the account's prior compliance review scope transfers —
confirm explicitly whether Legal treats generated customer language as
its own review category, before finalizing the schedule.
