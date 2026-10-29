# Report : Evaluating a Job Training Programme

**Important :** the data is synthetic , made for a simulated policy evaluation. Nothing here is evidence about a real Indian government programme.

Numbers are in [results.md](results.md) , code in `01_data_and_randomisation.ipynb` and `02_itt.ipynb`.

## Business understanding

A state skills mission offered subsidised training to applicants at random. Some of those offered never enrolled , and a few who were not offered enrolled anyway. Employment and earnings were recorded at 18 and 30 months. The government wants three answers :

1. What is the effect of **offering** training ?
2. What is the effect of the **training itself** ?
3. Do disadvantaged communities (OBC , SC , ST) benefit ?

The brief describes 10,000 applicants in 16 districts. The file it links to has 40,000 applicants in 45 districts (12 states) , and that file is used.

## 1. Data and randomisation

- 40,000 applicants , 25 columns. The only empty values are in `training_type` , and only for the 23,140 people who did not enrol , so they mean "no training".
- `training_type` and `months_in_training` are decided after the offer , so they are never used as controls.
- **Balance :** across 14 baseline characteristics (prior earnings and employment , schooling , age , marriage , dependants , BPL card , gender , area , age group , caste) the offered and not offered groups differ by at most 0.025 standard deviations. One p value of the 14 is below 0.05 , and about 0.7 are expected by chance.
- Exactly 2/3 of applicants were offered training in every state , so the offer was randomised within states. **Randomisation looks successful.**
- **Noncompliance :** 61.7% of those offered enrolled and 3.0% of those not offered enrolled anyway. The offer raised enrolment by 58.7 points. Being offered and being trained are not the same thing. A direct enrolled vs not enrolled comparison would mix the effect of training with who chooses to enrol.

## 2. Intent-to-Treat

The ITT compares everyone offered training with everyone not offered , whether or not they enrolled. Randomisation makes the two groups alike apart from the offer , so the gap is the causal effect of the offer.

- Employment : **+3.1 points** at 18 months , **+4.0 points** at 30 months.
- Earnings : **+6,551 INR** at 18 months , **+9,076 INR** at 30 months (95% CI 7,084 to 11,069). That is 13.5% above the group not offered.
- All p values are below 0.001 , and the effects grow between 18 and 30 months.

**For policymakers :** each applicant offered a place earns about 9,000 INR more at 30 months on average , counting the 38% who never took the place up.

## 3. Instrumental variables and LATE

Not done yet , see the last section.

## 4. Earnings , employment and subgroups

- **Zero earnings :** 57% of those not offered and 53% of those offered earn nothing at 30 months , and earnings are 0 exactly when someone is not employed. So the earnings ITT is partly "more people working" and partly "workers earning more". Comparing only the employed is not a fair comparison , because the offer changes who is employed.
- **Social categories :** at 30 months every group gains in both employment and earnings , with every 95% CI above 0. ST has the largest point estimates (+6.3 points , +11,961 INR) and also the widest intervals (the smallest group , 4,000). For ST the 18-month effects are not significant , so their gains show up later.
- The intervals overlap heavily. The data does not show that any one group gains more than another.
- **Multiple comparisons :** 16 subgroup tests at 5% would give about one false positive even with no real effects. After Bonferroni (each test at 0.05 / 16) , 12 of 16 stay significant , including all four 30-month earnings effects.

## 5. Recommendations (from the ITT so far)

- **Continue the programme.** Offering training raises employment and earnings , the effects are clearly significant , and they grow over time.
- **Statistical vs policy significance :** +9,076 INR is certain to be above 0 , but whether it is worth paying for depends on the cost per place offered , which is not in the data.
- **Targeting :** every caste group benefits , and the data cannot tell the groups' effects apart. On this evidence the programme should stay open to all groups rather than be narrowed to one.
- **Take-up :** 38% of offers are never used. Each offer that is not taken up dilutes the per-offer effect , so it is worth finding out why people decline.
- **Future evaluations :** record the cost per place , follow up for longer (the effects are still growing at 30 months) , and use larger samples for small groups like ST.

## Assumptions

- The offer was random (supported by the balance checks).
- One applicant's offer does not change another applicant's outcome.
- Outcomes are measured the same way for those offered and not offered.

## Limitations and next steps

- **Not done yet :** ITT with baseline covariates , the Wald estimator , 2SLS and the LATE (the effect of the training itself , question 2). These come next.
- No cost data , so no cost-benefit.
- Synthetic data.
