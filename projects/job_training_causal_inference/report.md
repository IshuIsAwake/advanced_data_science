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
- **Balance :** across 14 baseline characteristics (prior earnings and employment , schooling , age , marriage , dependants , BPL card , gender , area , age group , caste) the offered and not offered groups differ by at most 0.025 standard deviations. The largest gap (SC share) is also the only p value below 0.05 (p = 0.017). At alpha = 0.05 , 14 tests are expected to give 0.7 false positives , and with Bonferroni (0.05 / 14 = 0.00357) it doesn't pass.
- Exactly 2/3 of applicants were offered training in every state , so the offer was randomised within states. **Randomisation looks successful.**
- **Noncompliance :** 61.7% of those offered enrolled and 3.0% of those not offered enrolled anyway. The offer raised enrolment by 58.7 points. Being offered and being trained are not the same thing. A direct enrolled vs not enrolled comparison would mix the effect of training with who chooses to enrol.

## 2. Intent-to-Treat

The ITT compares everyone offered training with everyone not offered , whether or not they enrolled. Randomisation makes the two groups alike apart from the offer , so the gap is the causal effect of the offer.

- Employment : **+3.1 points** at 18 months , **+4.0 points** at 30 months.
- Earnings : **+6,551 INR** at 18 months , **+9,076 INR** at 30 months (95% CI 7,084 to 11,069). That is 13.5% above the group not offered.
- All p values are below 0.001. The standard errors are heteroskedasticity-robust (Welch's , the same as HC2 here).
- **Growth :** testing each person's change from 18 to 30 months , the earnings effect grows by 2,525 INR (95% CI 212 to 4,838 , p = 0.032). The employment effect grows by 0.84 points , which is not significant (p = 0.24). As a share of the not offered mean , the earnings effect barely moves (12.6% to 13.5%).

**For policymakers :** each applicant offered training earns about 9,000 INR more at 30 months on average , counting the 38% who never took it up.

## 3. Instrumental variables and LATE

Not done yet , see the last section.

## 4. Earnings , employment and subgroups

- **Zero earnings :** 57% of those not offered and 53% of those offered earn nothing at 30 months , and earnings are 0 exactly when someone is not employed. So the earnings ITT is partly "more people working" and partly "workers earning more" : of the 9,076 INR , 6,201 comes from the first and 2,875 from the second , as arithmetic. Comparing only the employed is not a fair comparison , because the offer changes who is employed : among the employed , offered workers have 0.11 fewer years of schooling (p = 0.02) and are 1.7 points more often female (p = 0.03).
- **Social categories :** at 30 months every group gains in both employment and earnings , with every 95% CI above 0. ST has the largest point estimates (+6.3 points , +11,961 INR) and also the widest intervals (the smallest group , 4,000). For ST the 18-month effects are not significant. Tested directly , ST's effects grow by 4.8 points (p = 0.035) and 7,870 INR (p = 0.021) , but neither passes a correction for the 8 such tests , so later gains are plausible , not firm.
- **Differences between groups :** none of the 24 gaps between group effects (6 pairs x 4 outcomes) is below 0.05 , and the smallest p is 0.10. So the data does not show that any one group gains more than another. It doesn't prove they are equal either : ST's lead over General on 30-month earnings is 3,632 INR , with a CI of -2,849 to 10,114. The offer raised enrolment by 57.7 to 59.5 points in every group , so any gaps are not down to take-up.
- **Multiple comparisons :** 16 subgroup tests at 5% would give about one false positive even with no real effects , and if they were independent there would be a 56% chance of at least one. After Bonferroni (each test at 0.05 / 16) , 12 of 16 stay significant , including all four 30-month earnings effects.

## 5. Recommendations (from the ITT so far)

- **Continue the programme.** Offering training raises employment and earnings , and the effects are clearly significant.
- **Statistical vs policy significance :** +9,076 INR is certain to be above 0 , but whether it is worth paying for depends on the cost per offer , which is not in the data.
- **Targeting :** every caste group benefits , and the data cannot tell the groups' effects apart. On this evidence the programme should stay open to all groups rather than be narrowed to one.
- **Take-up :** 38% of offers are never used. Each offer that is not taken up dilutes the per-offer effect , so it is worth finding out why people decline.
- **Future evaluations :** record the cost per offer , follow up for longer (the earnings effect was still rising in rupees at 30 months) , and use larger samples for small groups like ST.

## Assumptions

- The offer was random (supported by the balance checks).
- One applicant's offer does not change another applicant's outcome.
- Outcomes are measured the same way for those offered and not offered.

## Limitations and next steps

- **Not done yet :** ITT with baseline covariates , the Wald estimator , 2SLS and the LATE (the effect of the training itself , question 2). These come next.
- No cost data , so no cost-benefit.
- Synthetic data.
