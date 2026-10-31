# Results : Avazu Click Prediction

Every 40th row of the given train / valid / test files : 808,580 / 101,073 / 101,073 impressions , 1,356 one hot features (standardised). The numbers come from the notebooks in this folder , `05_sample_size_and_columns.ipynb` for the sample size and column tables.

## Data

| split | rows | CTR |
|---|---|---|
| train | 32,343,172 | 16.98% |
| valid | 4,042,897 | 16.98% |
| test | 4,042,898 | 16.98% |

## Test set

| model | log loss | ROC-AUC | PR-AUC | accuracy | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| baseline (always the train CTR) | 0.458 | 0.500 | 0.171 | 0.829 | - | 0 | 0 |
| **logistic regression** | **0.405** | **0.734** | **0.358** | 0.661 | 0.291 | 0.683 | 0.408 |
| logistic regression , class weighted | 0.603 | 0.734 | 0.357 | 0.668 | 0.293 | 0.666 | 0.407 |
| linear SVM , class weighted | - | 0.717 | 0.312 | 0.638 | 0.277 | 0.693 | 0.396 |

Thresholds picked by best F1 on validation : 0.19 (logistic) , 0.54 (weighted logistic) , 0.99 on the SVM score.

## Sample size and cut

Plain logistic regression , 500 epochs , all scored on the same 101,073 validation rows. Test is not used. A value below the cut goes into `other`. GPU peak has valid and test at 101,073 rows each.

| sample | cut | feature columns | train rows | one hot columns | GPU peak | log loss | ROC-AUC |
|---|---|---|---|---|---|---|---|
| 1 in 128 | 0.1% | 18 | 252,682 | 707 | 1.31 GB | 0.40671 | 0.72518 |
| 1 in 64 | 0.1% | 18 | 505,363 | 705 | 2.02 GB | 0.40599 | 0.72641 |
| 1 in 32 | 0.1% | 18 | 1,010,725 | 703 | 3.45 GB | 0.40571 | 0.72705 |
| 1 in 20 | 0.1% | 18 | 1,617,159 | 703 | 5.17 GB | 0.40575 | 0.72706 |
| 1 in 45 | 0.025% | 18 | 718,738 | 1,475 | 5.50 GB | 0.40199 | 0.73443 |
| 1 in 40 | 0.025% | 18 | 808,580 | 1,464 | does not fit | 0.40176 | 0.73472 |
| 1 in 32 | 0.025% | 18 | 1,010,725 | 1,468 | does not fit | 0.40146 | 0.73563 |
| 1 in 20 | 0.025% | 18 | 1,617,159 | 1,468 | does not fit | 0.40131 | 0.73569 |
| **1 in 40 (final)** | **0.025%** | **15** | **808,580** | **1,356** | **5.55 GB** | **0.40190** | **0.73454** |

- More rows alone barely help : at 0.1% , 1 in 128 to 1 in 32 gains 0.0010 and 1 in 20 gains nothing more.
- The cut helps far more : at 1 in 32 , 0.1% to 0.025% gains 0.0043.
- The final setting gives up 0.0006 against 1 in 20 at 0.025% , which doesn't fit.

Share of rows in `other` (1 in 40) :

| column | cut 0.1% | cut 0.025% |
|---|---|---|
| device_model | 29.6% | 13.1% |
| site_id | 11.6% | 5.8% |
| site_domain | 8.8% | 4.7% |
| app_id | 7.7% | 4.5% |
| C17 | 6.8% | 1.5% |

## Columns

Against the final setting (log loss 0.40190). Cost = how much log loss rises without the column.

| left out | columns saved | cost |
|---|---|---|
| C1 | 5 | 0.00001 |
| C18 | 3 | 0.00001 |
| app_domain | 24 | 0.00006 |
| C21 | 50 | 0.00007 |
| C19 | 55 | 0.00009 |
| C18 , C19 , C21 together | 108 | 0.00013 |
| C14 (the model doesn't fit with it) | 421 | 0.00094 |

| kept | columns it takes | cost if dropped |
|---|---|---|
| C15 | 4 | -0.00001 |
| weekday | 6 | 0.00000 |
| device_conn_type | 3 | 0.00000 |
| device_type | 3 | 0.00002 |
| banner_pos | 4 | 0.00009 |
| C16 | 5 | 0.00009 |
| C20 | 93 | 0.00013 |
| app_category | 13 | 0.00013 |
| site_category | 13 | 0.00015 |
| hour_of_day | 23 | 0.00018 |
| site_domain | 146 | 0.00038 |
| site_id | 182 | 0.00101 |
| device_model | 487 | 0.00179 |
| C17 | 248 | 0.00343 |
| app_id | 126 | 0.00374 |

Dropping C20 instead of C21 saves 43 more columns , but log loss is 0.00004 higher. Gaps under about 0.0001 are too small to read much into on 101,073 rows.

## Sample vs all rows

| hour | rows (all) | rows (sample) | clicks (all) | clicks (sample) | CTR (all) | CTR (sample) |
|---|---|---|---|---|---|---|
| quietest , 24 Oct 22:00 | 11,877 | 298 | 1,825 | 50 | 15.37% | 16.78% |
| busiest , 22 Oct 09:00 | 358,731 | 8,967 | 50,033 | 1,250 | 13.95% | 13.94% |

All 240 hours are in the sample , the largest gap from all / 40 is 3.2 rows , CTR per hour is 0.55 points off on average and 2.01 at most , and 95% of hours are within 2 standard errors.

## How columns go together

| pair | correlation on the codes | Cramér's V |
|---|---|---|
| C14 , C15 | 0.00 | 1.00 |
| C14 , C16 | 0.04 | 1.00 |
| C14 , C21 | 0.41 | 1.00 |
| C14 , C17 | 0.98 | 1.00 |
| C17 , C21 | 0.42 | 1.00 |
| C17 , C18 | -0.25 | 0.99 |
| C17 , C19 | -0.13 | 0.87 |
| C1 , device_type | 0.89 | 0.82 |

Our `cramers_v` gives 0.816497 for C1 , device_type , the same as scipy.

## Logistic regression

- Gradient descent , 2000 epochs at the largest safe learning rate (`max_lr`). Final loss 0.4015 train , 0.4019 validation.
- sklearn `LogisticRegression` (no penalty) on the same data gives the same test numbers to 3 decimals.

Confusion matrix (test , threshold 0.19) :

| | predicted no click | predicted click |
|---|---|---|
| no click | 54,954 | 28,824 |
| click | 5,478 | 11,817 |

## Calibration (test , 10 bins by predicted probability)

| bin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| predicted (plain) | 0.018 | 0.043 | 0.069 | 0.100 | 0.136 | 0.171 | 0.206 | 0.240 | 0.292 | 0.427 |
| actual CTR | 0.018 | 0.043 | 0.073 | 0.100 | 0.134 | 0.178 | 0.216 | 0.241 | 0.296 | 0.411 |
| predicted (weighted) | 0.081 | 0.178 | 0.264 | 0.348 | 0.433 | 0.501 | 0.557 | 0.607 | 0.669 | 0.778 |

| | mean prediction | log loss | ROC-AUC |
|---|---|---|---|
| plain | 0.170 | 0.4051 | 0.7343 |
| weighted | 0.442 | 0.6026 | 0.7342 |
| weighted , log(c_pos / c_neg) taken off the bias | 0.170 | 0.4052 | 0.7342 |

## SVM (class weighted)

Validation ROC-AUC by C : 0.001 -> 0.7159 , **0.01 -> 0.7175** , 0.03 -> 0.7159 , 0.1 -> 0.7121.
Learning rate lowered in steps (0.1 , 0.03 , 0.01 , 0.003 , 500 epochs each).
sklearn `SGDClassifier` (hinge , alpha = C , balanced) with its own threshold from validation : test ROC-AUC 0.713 against our 0.717 , PR-AUC 0.312 for both , F1 0.394 against 0.396. F1 is flat near its best , so the two thresholds land on different recall (0.616 against 0.693).
