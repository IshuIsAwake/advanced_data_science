# Results : Job Training Programme

Synthetic data , 40,000 applicants. ITT = mean of those offered training - mean of those not offered. 95% CIs and p values use the unequal-variance (Welch) standard error , from `self_module/stats.py`. It is heteroskedasticity-robust , and equals HC2 for a two-group comparison. All numbers come from `02_itt.ipynb` and `01_data_and_randomisation.ipynb`.

## Assignment and enrolment

| | not enrolled | enrolled | total | enrolment rate |
|---|---|---|---|---|
| not offered | 12,927 | 406 | 13,333 | 3.0% |
| offered | 10,213 | 16,454 | 26,667 | 61.7% |

First stage (offer -> enrolment) : **+58.7 points** , 95% CI 58.0 to 59.3.

## Balance

14 baseline characteristics. Largest gap 0.025 standard deviations (SC share). 1 of 14 p values below 0.05 (SC share , p = 0.017) , about 0.7 expected by chance. With Bonferroni (0.05 / 14 = 0.00357) none passes. Exactly 2/3 offered in every state.

## ITT

| outcome | offered | not offered | ITT | 95% CI | p |
|---|---|---|---|---|---|
| employed at 18 months | 46.2% | 43.1% | +3.1 pts | 2.1 to 4.1 | < 0.001 |
| employed at 30 months | 46.9% | 43.0% | +4.0 pts | 2.9 to 5.0 | < 0.001 |
| earnings at 18 months (INR) | 58,712 | 52,161 | +6,551 | 5,036 to 8,067 | < 0.001 |
| earnings at 30 months (INR) | 76,406 | 67,329 | +9,076 | 7,084 to 11,069 | < 0.001 |

Welch's df is 28,032 for 30-month earnings , where the value for 95% is 1.96005 for t and 1.95996 for the normal.

Change from 18 to 30 months , each person's change , offered vs not offered :

| outcome | change in the effect | 95% CI | p |
|---|---|---|---|
| employment | +0.84 pts | -0.57 to 2.25 | 0.241 |
| earnings (INR) | +2,525 | 212 to 4,838 | 0.032 |

The earnings ITT is 12.6% of the not offered mean at 18 months and 13.5% at 30 months.

## Zero earnings

At 30 months : 57.0% of those not offered , 53.1% of those offered (earnings are 0 exactly when not employed).

| | share employed | earnings of the employed (INR) | mean earnings (INR) |
|---|---|---|---|
| offered | 46.93% | 162,793 | 76,406 |
| not offered | 42.98% | 156,667 | 67,329 |

Of the 9,076 INR , 6,201 is more people working and 2,875 is offered workers earning more. The split is arithmetic , not an effect on pay.

Offered minus not offered , among everyone and among those employed at 30 months :

| baseline | everyone | p | employed | p |
|---|---|---|---|---|
| prior earnings (INR) | -27 | 0.958 | -893 | 0.276 |
| employed before | 0.002 | 0.666 | -0.007 | 0.380 |
| years of schooling | -0.020 | 0.537 | -0.110 | 0.020 |
| age | 0.016 | 0.814 | -0.016 | 0.874 |
| female | 0.008 | 0.148 | 0.017 | 0.027 |

## ITT by social category

| group | n | employed 18m | employed 30m | earnings 18m (INR) | earnings 30m (INR) |
|---|---|---|---|---|---|
| General | 20,000 | +3.6 (2.1 , 5.1) | +3.5 (2.1 , 5.0) | +6,687 (4,457 , 8,916) | +8,329 (5,414 , 11,244) |
| OBC | 8,800 | +2.4 (0.2 , 4.6) | +5.1 (2.9 , 7.3) | +6,871 (3,695 , 10,046) | +9,736 (5,480 , 13,991) |
| SC | 7,200 | +4.0 (1.6 , 6.4) | +2.9 (0.5 , 5.4) | +8,229 (4,938 , 11,520) | +10,097 (5,794 , 14,400) |
| ST | 4,000 | +1.5 (-1.7 , 4.8) | +6.3 (3.1 , 9.5) | +4,091 (-321 , 8,504) | +11,961 (6,172 , 17,751) |

Employment in points , 95% CI in brackets. With Bonferroni over the 16 tests (each at 0.05 / 16) , 12 stay significant. The ones lost are OBC employment at 18 months , SC employment at 30 months , and both ST 18-month effects.

**Gaps between groups :** 6 pairs x 4 outcomes = 24 gaps , none below 0.05 , smallest p 0.104 (SC against ST on employment at 30 months) , about 1.2 expected by chance. ST minus General on 30-month earnings : 3,632 INR , 95% CI -2,849 to 10,114 , p = 0.272.

**First stage by group :** General 58.6 , OBC 59.5 , SC 57.7 , ST 58.7 points.

**Change from 18 to 30 months by group :**

| group | employment (pts) | p | earnings (INR) | p |
|---|---|---|---|---|
| General | -0.08 | 0.937 | +1,642 | 0.346 |
| OBC | +2.69 | 0.080 | +2,865 | 0.251 |
| SC | -1.05 | 0.536 | +1,868 | 0.466 |
| ST | +4.77 | 0.035 | +7,870 | 0.021 |

With 8 tests , the corrected line is 0.05 / 8 = 0.00625 , and none passes it.

## Not done yet

ITT with baseline covariates , the Wald estimator , 2SLS and LATE.
