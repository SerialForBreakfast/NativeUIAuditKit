# Research discovery and actionable follow-ups

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.

## Added investigations

These are locally motivated hypotheses, not verified claims from a new paper.
They remain preparation records until their named inputs and adapter variants qualify.

| Record | Test | Decision |
| --- | --- | --- |
| B405-195 | Add a fixed teacher penalty on old training examples during native adaptation. | Can we preserve earlier behavior without preventing native gains? |
| B405-196 | Compare measured training proposal errors with generic crop jitter. | Does realistic box-error training improve deployable selection? |
| B405-197 | Compare more scene groups with more views per scene at equal frame count. | Should capture effort prioritize new layouts or repeated views? |
| B405-198 | Change surrounding context while preserving control pixels and scale. | Does context cause false focus decisions? |

Prioritize B405-196 after proposal correspondence qualifies. Reuse prior jitter controls only when exposure and settings match.
B405-197 extends the shared subset producer. It differs from B405-190, which tests transfer between control families.
B405-198 isolates context without resizing the control. It differs from earlier margin tests that change effective control scale.
B405-195 remains conditional on a qualified training variant and a persistent regression that simpler geometry correction cannot resolve.
Keep Standard unchanged and HCF optional. No new capture or fit starts from these records.
Diagnostics retain 800 s and 100 MB limits. Record explicit fit budgets before approval.

## Recommended discovery sources

See [the 70-idea source review](ResearchSources417.md) for 10 ideas from each of 7 discovery sources.
The review maps proposals to existing experiments. It does not add execution approvals.

These rankings reflect project fit, not measured source quality.

| Priority | Source | Use | Limit |
| --- | --- | --- | --- |
| High | [OpenReview](https://openreview.net/) | Methods, reviews, revisions, and reproducibility concerns. | Review visibility varies by venue; acceptance does not establish local benefit. |
| High | [PMLR](https://proceedings.mlr.press/) | Conference and workshop methods with stable proceedings. | Check task, assumptions, and code before transfer. |
| High | [CVF Open Access](https://openaccess.thecvf.com/) | Computer-vision methods and evaluation papers. | Direct access returned 403 during this review; no specific new paper is verified here. |
| High | Apple documentation, WWDC, and author repositories | Runtime behavior, conversion constraints, reference code, and reported failures. | Separate official API contracts from user reports and device-specific claims. |
| Medium | [Hugging Face Papers](https://huggingface.co/papers/trending) | Discover papers and related artifacts quickly. | Popularity is not quality or reproduction evidence. |
| Medium | [r/computervision](https://www.reddit.com/r/computervision/) and [r/MachineLearning](https://www.reddit.com/r/MachineLearning/) | Practical failure reports, comparisons, and links to original work. | Comments are leads, not verified performance evidence. |
| Medium | [Hacker News](https://news.ycombinator.com/) | Tool design, deployment costs, reproducibility, and operational lessons. | General discussion has uneven relevance to vision training. |
| Occasional | [Two Minute Papers](https://www.youtube.com/@TwoMinutePapers) | Discover visual methods through short demonstrations. | Read the underlying paper and limitations before defining a test. |
| Low | [Slashdot](https://slashdot.org/) | Broad technology context. | Use selectively; it is not the main source for detailed vision methods. |

## Turn a discovery into a useful experiment

1. Record the original paper or official implementation, not only the community link.
2. Check the date, revision, code license, data terms, and actual task.
3. Name the observed NUIAK failure that the idea could address.
4. Search the catalog for existing answers and related experiments.
5. Specify one controlled change and a decision that affects our next action.
6. Prefer cached diagnostics before adding capture or training.
7. Name missing template variants and inputs explicitly.
8. Keep outside claims separate from local measurements.

Do not download unknown checkpoints or run repository scripts during discovery.
Do not upload private captures to community services.
Do not use votes, demonstrations, or benchmark rankings as promotion evidence.
No recurring monitoring or subscriptions are enabled by this document.
