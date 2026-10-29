# Report : Digital Advertising Click Prediction

Numbers are in [results.md](results.md) , code in the four notebooks of this folder. The models are written from scratch in `self_module/` (logistic regression , weighted logistic regression , weighted linear SVM) and checked against sklearn.

## 1. Business understanding

An ad platform shows ads on websites and inside apps and is paid when an ad is clicked. The **problem** is to tell which impressions are likely to be clicked , so the budget goes to the impressions that pay.

- **Target :** `click` (1 = clicked). Binary classification.
- **Questions :** what share of impressions get clicked , which devices / apps / sites / positions / hours click more , can a model rank impressions better than a guess , and where should the budget go.

## 2. Dataset summary and EDA

- Avazu click logs : 40.4 million impressions over 10 days (21 to 30 Oct 2014) , given as train / valid / test (80 / 10 / 10). CTR is 16.98% in all three , so the split looks stratified on click.
- **Sampling :** every 32nd row of each file is used (1.01 M train , 126 k valid , 126 k test). The rows are in time order , so the sample covers every hour.
- **Variables :** 24 columns , all categories stored as codes or hashes , even the ones that look numeric. site / app / device describe where and to whom the ad is shown , C14 to C21 are anonymised. The summary tool (`dfSummary`) is in `01_eda.ipynb`.
- **Missing values :** no NaNs , but placeholders : device_id `a99f214a` on 82% of rows and C20 = -1 on 47%. They are kept as their own level.
- **Class distribution :** 17% clicks. Always guessing "no click" scores 83% accuracy , so log loss , ROC-AUC and PR-AUC are used instead of accuracy.

| feature | CTR finding |
|---|---|
| website vs app | websites 19.9% , apps 11.9% |
| device_type | type 0 21.1% , type 1 (92% of traffic) 16.9% , types 4 and 5 about 9% |
| device_conn_type | type 0 (86% of traffic) 18.1% , types 3 and 5 below 5% |
| site_category | from 28.2% (3e814130) down to 3% (76b2941d) |
| banner_pos | position 0 16.4% , position 1 18.4% |
| hour / weekday | only 16% to 18.5% |

- **Correlation :** C14 and C17 are 0.98 correlated (each C14 has exactly one C17) , C1 and device_type 0.89. One of each pair is dropped. No single code is strongly correlated with click.

## 3. Machine learning

- **Feature engineering :** `hour` becomes hour of day and weekday.
- **Feature selection :** dropped `id` (row key) , `device_id` and `device_ip` (hundreds of thousands of levels that identify users , not kinds of impressions) , `C14` (repeats C17) , `C1` (repeats device_type) and `app_domain` (fixed by app_id).
- **Rare levels :** any level in fewer than 0.1% of train rows becomes `other`. One hot encoding then gives 703 columns , all standardised with train statistics only.
- **Leakage :** the kept levels , the one hot columns and the scaler all come from train. Valid is used for the threshold and for C. Test is used once.
- **Models :**
  - a baseline that always predicts the train CTR
  - logistic regression
  - class weighted logistic regression (each class carries half the loss)
  - class weighted linear SVM , with C tuned on validation

  All three fitted models use full batch gradient descent on the GPU.

**Test results** (126,341 impressions , threshold for precision / recall / F1 picked by best F1 on validation) :

| model | log loss | ROC-AUC | PR-AUC | precision | recall | F1 |
|---|---|---|---|---|---|---|
| baseline (always the train CTR) | 0.456 | 0.500 | 0.170 | - | 0 | 0 |
| **logistic regression** | **0.409** | **0.725** | **0.347** | 0.285 | 0.679 | 0.401 |
| logistic regression , class weighted | 0.611 | 0.724 | 0.345 | 0.283 | 0.683 | 0.400 |
| linear SVM , class weighted (C = 0.01) | - | 0.704 | 0.312 | 0.266 | 0.693 | 0.384 |

The SVM gives a score , not a probability , so it has no log loss. Each model was checked against sklearn on the same data (`LogisticRegression` with no penalty , `SGDClassifier` with the hinge loss) and gives the same numbers to about 0.005.

## 4. Inference and interpretation

- **Performance :** plain logistic regression is the best model. Its log loss is 0.409 against 0.456 for the baseline (10% lower) , ROC-AUC 0.725 and PR-AUC 0.347 (the base rate is 0.17). Train and test agree , so it is not overfitting , and our model matches sklearn's to 3 decimals.
- **Ranking :** the 10% of test impressions the model rates highest are clicked 40% of the time , the lowest 10% only 2.5% of the time. That is a 16x gap.
- **Calibration :** the plain model's probabilities match the real CTR in every decile (it says 41% , reality is 40%). Class weighting does not rank any better (ROC-AUC 0.724) and pushes every probability up (mean 0.45 against a real 0.17) , which is why its log loss is 0.611. Taking log(c_pos / c_neg) off the bias undoes it (log loss back to 0.409 , the same as the plain model). For an ad platform the probability goes straight into the bid , so calibration matters more than any threshold.
- **SVM :** it ranks worse than logistic regression and gives a score instead of a probability , so it can't price an impression.
- **Important features :** site and app categories , specific sites and apps , banner position 1 , and some C17 / C21 levels. Many one hot columns overlap (a site sits inside a category) , so a weight is the effect with the other columns held fixed , not the raw CTR gap.
- **Predictive vs causal :** websites click more than apps , and position 1 more than position 0 , but ads are not placed at random. Advertisers , publishers and the platform choose where each ad goes and who sees it , so a high CTR in position 1 may just mean better ads get position 1. The model finds which impressions tend to get clicked. Whether moving an ad changes its clicks needs an experiment (an A/B test that randomises the placement).
- **Limitations :**
  - 1 in 32 rows used.
  - Rare levels merged into `other`.
  - The features are hashed and anonymised , so they are hard to explain to the business.
  - Only 10 days. The given split is random , so test comes from the same days as train , and new days will probably score a bit worse.
  - A linear model misses combinations (this app on this device).
  - No user history , since device_id and device_ip were dropped.

## 5. Recommendations

1. **Score every impression with the plain logistic model and bid by expected value** , P(click) x price per click. Its probabilities are calibrated , so they can be used directly.
2. **Put the budget on the top of the ranking.** The top 30% by predicted probability click at about 31% , the bottom 30% at about 5%.
3. **Shift spend between segments , but test it first.**
   - Website inventory (20% CTR) beats in-app (12%).
   - Connection type 0 and device type 0 beat the rest.
   - Connection types 3 / 5 , device types 4 / 5 and the weakest site categories (f66779e6 , 76b2941d , below 4%) are the first places to cut.

   These are associations , so move a small share of budget in an A/B test before moving the rest.
4. **Don't bid with a class weighted model.** If weights are used for a yes / no rule , take log(c_pos / c_neg) off the bias first.
5. **Next steps :**
   - Train on all 40 million rows.
   - Add models that learn combinations of features (factorisation machine , neural network , boosting).
   - Add user-history features (how often a device_ip / device_id appears) , computed on train only.
   - Validate on the last day instead of a random split.
