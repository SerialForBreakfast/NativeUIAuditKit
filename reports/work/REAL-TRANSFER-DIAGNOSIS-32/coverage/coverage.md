# Training coverage versus reviewed controls

Verified 1250 source pairs, including 1000 training pairs.
Training body width/height range: 1.084–1.761.
Layout names: {'row': 1000}. A layout named row is not a Settings listRow control.

| Real pair | Width/height | Outside training range | Context clipped |
| --- | --- | --- | --- |
| review-1 | 9.604 | True | True |
| review-2 | 1.643 | False | False |
| review-3 | 7.140 | True | False |
| review-4 | 10.651 | True | True |
| review-5 | 10.000 | True | True |
| review-8 | 11.049 | True | True |
| photos | 1.656 | False | False |
| music | 1.674 | False | False |

Metadata coverage mismatch is not causal proof; native control rendering and appearance also differ.
