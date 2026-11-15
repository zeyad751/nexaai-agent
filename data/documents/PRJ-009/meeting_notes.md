# Meeting Notes: Clinical AI Rollout — Mid-Project Crisis Review
**Date:** April 10, 2023
**Attendees:** Khaled Naguib (NexaAI PM), Ola El-Sayed (NexaAI, AI
Engineering), Nileside Chief Medical Information Officer, Nileside
department heads (Cardiology, Dermatology, Pediatrics)

## Discussion
Six weeks into network-wide data aggregation, Ola El-Sayed reported that
initial model training runs were performing far worse than the pilot
department's results — well below the accuracy needed for physician
trust. Investigation traced this to a data quality issue the original
proposal had not anticipated: the pilot department's notes turned out to
follow an unusually disciplined, template-driven documentation style
specific to that department's senior physicians, which was not
representative of documentation practice across the rest of the network.
Other departments' notes were far more free-form, abbreviated, and
inconsistent — a single network-wide model trained naively across all of
it was learning noise rather than signal.

The Cardiology department head noted, somewhat pointedly, that the pilot
had effectively been run on "best-case" data and asked whether the whole
network-wide approach was now in question.

Khaled Naguib acknowledged the original scale-up assumption — that the
pilot's data characteristics would generalize — had not held, and that
continuing to push the single-model-training approach against this data
reality risked missing the year-end target entirely without addressing
the root problem.

## Decision (Strategy Pivot — Negative outcome logged for the original approach)
The team agreed to abandon the single-custom-model-training approach in
its original form. This was logged as a negative-outcome decision for the
original plan: the assumption behind it did not hold, and continuing
would not have produced a usable network-wide capability on any
reasonable timeline.

## Revised Direction
Rather than training one large custom model, the team proposed pivoting
to a **Product-Led AI** approach: a retrieval-augmented system built on a
commercial LLM API, with department-specific prompt and retrieval tuning
rather than department-specific model retraining, and an internal
Nileside product owner assigned to continue iterating after NexaAI's
engagement ends. This shifts the engagement from "deliver one finished
model" to "stand up an evolving capability Nileside can keep improving."

## Action Items
- NexaAI to prototype the retrieval-based approach against Cardiology and
  Dermatology data within three weeks
- Nileside to name an internal clinical informatics owner to co-own the
  capability going forward
