# Results : Avazu Click Prediction

Every 32nd row of the given train / valid / test files : 1,010,725 / 126,341 / 126,341 impressions , 703 one hot features (standardised). All numbers come from `03_logistic_regression.ipynb` and `04_svm.ipynb`.

## Data

| split | rows | CTR |
|---|---|---|
| train | 32,343,172 | 16.98% |
| valid | 4,042,897 | 16.98% |
| test | 4,042,898 | 16.98% |

## Test set

| model | log loss | ROC-AUC | PR-AUC | accuracy | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| baseline (always the train CTR) | 0.456 | 0.500 | 0.170 | 0.830 | - | 0 | 0 |
| **logistic regression** | **0.409** | **0.725** | **0.347** | 0.655 | 0.285 | 0.679 | 0.401 |
| logistic regression , class weighted | 0.611 | 0.724 | 0.345 | 0.651 | 0.283 | 0.683 | 0.400 |
| linear SVM , class weighted | - | 0.704 | 0.312 | 0.621 | 0.266 | 0.693 | 0.384 |

Thresholds picked by best F1 on validation : 0.19 (logistic) , 0.53 (weighted logistic) , 0.73 on the SVM score.

## Logistic regression

- Gradient descent , 2000 epochs at the largest safe learning rate (`max_lr`). Final loss 0.407 train , 0.409 validation.
- sklearn `LogisticRegression` (no penalty) on the same data gives the same test numbers to 3 decimals.

Confusion matrix (test , threshold 0.19) :

| | predicted no click | predicted click |
|---|---|---|
| no click | 68,143 | 36,688 |
| click | 6,903 | 14,607 |

## Calibration (test , 10 bins by predicted probability)

| bin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| predicted (plain) | 0.021 | 0.047 | 0.074 | 0.105 | 0.137 | 0.173 | 0.207 | 0.239 | 0.287 | 0.409 |
| actual CTR | 0.025 | 0.050 | 0.073 | 0.104 | 0.134 | 0.172 | 0.213 | 0.247 | 0.286 | 0.398 |
| predicted (weighted) | 0.097 | 0.193 | 0.278 | 0.362 | 0.436 | 0.504 | 0.560 | 0.605 | 0.663 | 0.765 |

| | mean prediction | log loss | ROC-AUC |
|---|---|---|---|
| plain | 0.170 | 0.4087 | 0.7247 |
| weighted | 0.446 | 0.6108 | 0.7242 |
| weighted , log(c_pos / c_neg) taken off the bias | 0.170 | 0.4090 | 0.7242 |

## SVM (class weighted)

Validation ROC-AUC by C : 0.001 -> 0.7021 , **0.01 -> 0.7069** , 0.03 -> 0.7049 , 0.1 -> 0.7009.
Learning rate lowered in steps (0.1 , 0.03 , 0.01 , 0.003 , 500 epochs each). sklearn `SGDClassifier` (hinge , alpha = C , balanced) : test ROC-AUC 0.702 against our 0.704.
