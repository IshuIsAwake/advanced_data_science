# Advanced Data Science Assignment

**Repository :** https://github.com/IshuIsAwake/advanced_data_science

Ishan Batra , 240485

Two decision problems from the ADS assignment , one folder each under `projects/`.
Each report follows BADIR : Business understanding , Analysis , Data insights , Inference , Recommendations.

| part | folder | problem |
|---|---|---|
| 1 | `projects/ctr_competition/` | which ad impressions get clicked (Avazu click logs) |
| 2 | `projects/job_training_causal_inference/` | what a randomised offer of job training did to employment and earnings |

## How the repo is organised

```
README.md                             this file
REPRODUCE.md                          environment , data download and the order to run things
requirements.txt
self_module/                          models and estimators written from scratch in PyTorch , the maths is in the comments
projects/
    ctr_competition/                  part 1
        *.ipynb                       notebooks , run in numbered order
        report.md                     the write up
        results.md                    final numbers
    job_training_causal_inference/    part 2
        *.ipynb
        report.md
        results.md
data/                                 git-ignored , filled by the steps in REPRODUCE.md
docs/                                 the assignment brief
```
