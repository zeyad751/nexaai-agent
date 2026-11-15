# Post-Mortem: Generative AI Marketing Content Engine
**Date:** July 2024
**Status at close:** Completed 16 days behind the original plan; actual
cost $713.9K against a $606.3K budget (~18% over) — recovered strongly
from a weak start (overall project score climbed from 34.8 to 64.2)

## What Happened
The original fully-autonomous content generation design was abandoned
within the first two months after regional marketing leads rejected
several generated pieces as off-brand or generic (see October 2023
meeting notes) — a reputational risk the client was unwilling to accept
regardless of potential future improvement through prompt iteration
alone. The subsequent pivot to a human-in-the-loop review workflow
turned the engagement around: satisfaction climbed from 3.8 to 7.3 and
adoption from 10.5% to 66.4% by close.

## Root Cause
The original design assumed brand voice consistency could be converged
on through prompt iteration alone, without a human review step. This
underestimated how much regional brand positioning — built over years
and varying meaningfully market to market — requires human judgment
that a purely automated pipeline, however well-tuned, was not going to
reliably replicate on its own.

## What Worked
The pivot to human-in-the-loop review did not just fix the immediate
brand-risk problem — it also gave the team a much better feedback signal
for iterating the underlying generation prompts, since reviewer edits
directly showed where and how generated drafts missed the mark. This
made the Build-Measure-Learn approach work as intended, once the loop
actually included a human measurement step.

## Lessons Learned
For any generative content engine where brand consistency or
reputational risk is a live concern, do not scope a fully-autonomous,
no-review pipeline on the assumption that prompt iteration alone will
converge on acceptable quality — build the human review step in from the
start as both a risk control and, as it turned out here, a better
source of iteration signal than pure prompt experimentation.
