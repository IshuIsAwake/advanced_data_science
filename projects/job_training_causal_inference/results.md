# Results : Job Training Programme

Synthetic data , 40,000 applicants. ITT = mean of those offered training - mean of those not offered. 95% CIs and p values use the unequal-variance (Welch) standard error , from `self_module/stats.py`. All numbers come from `02_itt.ipynb` and `01_data_and_randomisation.ipynb`.

## Assignment and enrolment

| | not enrolled | enrolled | total | enrolment rate |
|---|---|---|---|---|
| not offered | 12,927 | 406 | 13,333 | 3.0% |
| offered | 10,213 | 16,454 | 26,667 | 61.7% |

First stage (offer -> enrolment) : **+58.7 points** , 95% CI 58.0 to 59.3.

## Balance

14 baseline characteristics. Largest gap 0.025 standard deviations (SC share). 1 of 14 p values below 0.05 (SC share , p = 0.017) , about 0.7 expected by chance. Exactly 2/3 offered in every state.

## ITT

| outcome | offered | not offered | ITT | 95% CI | p |
|---|---|---|---|---|---|
| employed at 18 months | 46.3% | 43.1% | +3.1 pts | 2.1 to 4.2 | < 0.001 |
| employed at 30 months | 46.9% | 43.0% | +4.0 pts | 2.9 to 5.0 | < 0.001 |
| earnings at 18 months (INR) | 58,712 | 52,161 | +6,551 | 5,036 to 8,067 | < 0.001 |
| earnings at 30 months (INR) | 76,406 | 67,329 | +9,076 | 7,084 to 11,069 | < 0.001 |

Zero earnings at 30 months : 57.0% of those not offered , 53.1% of those offered (earnings are 0 exactly when not employed).

## ITT by social category

| group | n | employed 18m | employed 30m | earnings 18m (INR) | earnings 30m (INR) |
|---|---|---|---|---|---|
| General | 20,000 | +3.6 (2.1 , 5.1) | +3.5 (2.1 , 5.0) | +6,687 (4,457 , 8,916) | +8,329 (5,414 , 11,244) |
| OBC | 8,800 | +2.4 (0.2 , 4.6) | +5.1 (2.9 , 7.3) | +6,871 (3,695 , 10,046) | +9,736 (5,480 , 13,991) |
| SC | 7,200 | +4.0 (1.6 , 6.4) | +2.9 (0.5 , 5.4) | +8,229 (4,938 , 11,520) | +10,097 (5,794 , 14,400) |
| ST | 4,000 | +1.5 (-1.7 , 4.8) | +6.3 (3.1 , 9.5) | +4,091 (-321 , 8,504) | +11,961 (6,172 , 17,751) |

Employment in points , 95% CI in brackets. With Bonferroni over the 16 tests (each at 0.05 / 16) , 12 stay significant. The ones lost are OBC employment at 18 months , SC employment at 30 months , and both ST 18-month effects.

## Not done yet

ITT with baseline covariates , the Wald estimator , 2SLS and LATE.
