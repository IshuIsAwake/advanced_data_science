# Report : Digital Advertising Click Prediction

Numbers are in [results.md](results.md).

## 1. Business understanding

An ad platform shows ads on websites and inside apps and is paid when an ad is clicked. The **problem** is to tell which impressions are likely to be clicked , so the budget goes to the impressions that pay.

- **Target :** `click` (1 = clicked). Binary classification.
- **Questions :** what share of impressions get clicked , which devices / apps / sites / positions / hours click more , can a model rank impressions better than a guess , and where should the budget go.

## 2. Dataset summary and EDA

- Avazu click logs from the [Kaggle competition](https://www.kaggle.com/c/avazu-ctr-prediction/data) : 40.4 million impressions over 10 days (21 to 30 Oct 2014) , given as train / valid / test (80 / 10 / 10). CTR is 16.98% in all three , so the split looks stratified on click.
- **The competition :** Kaggle scored on log loss , since a platform bids with the probability itself. The winners (4 Idiots) used field-aware factorization machines in a 20 model ensemble , and the part they released scored 0.3797 on the next day. Our test is a random part of the same 10 days , so the two can't be compared.
- **Sampling :** every 40th row of each file is used (809 k train , 101 k valid , 101 k test) , because that is what fits in the GPU once one hot encoded. All 40 million rows come later , with batching and a neural network written from scratch.
- **Is the sample representative :** the quietest hour has 11,877 rows in all and 298 in the sample , the busiest 358,731 and 8,967 , and they are the same hours in both. No hour is more than 3.2 rows from all / 40. CTR per hour is 0.55 points off on average , and 95% of hours are within 2 standard errors , which is what chance gives.
- **Variables :** 24 columns , all categories stored as codes or hashes , even the ones that look numeric. site / app / device describe where and to whom the ad is shown , C14 to C21 are anonymised. The summary tool (`dfSummary`) is in `01_eda.ipynb`.
- **How a row is laid out :** every row has every column filled. App rows hold one fixed set of values in the site columns (`85f751fd` , `c4e18dd6` , `50e219e0`) , website rows hold one fixed set in the app columns (`ecad2386` , `7801e8d9` , `07d7df22`). So site categories are read on website rows only , and app categories on app rows only : `50e219e0` looks like 13% CTR on all rows , but 88% of those rows are app placeholders and on real websites it is 20%.
- **Missing values :** no NaNs , but placeholders : device_id `a99f214a` on 82.5% of rows (with 377,512 IPs and 3,569 device models , which one device can't have) and C20 = -1 on 47% (every other value is between 100000 and 100248). C20 = -1 has 19.4% CTR against 14.9% , so it stays as its own value. All of this is read from the pattern , no data dictionary defines these values.
- **Class distribution :** 17% clicks. Always guessing "no click" scores 83% accuracy , so log loss , ROC-AUC and PR-AUC are used instead of accuracy.

| feature | CTR finding |
|---|---|
| website vs app | websites 19.8% , apps 12.0% |
| device_type | type 0 20.9% , type 1 (92% of traffic) 16.9% , types 4 and 5 about 9.5% |
| device_conn_type | type 0 (86% of traffic) 18.1% , types 3 and 5 below 5% |
| site_category (website rows) | from 28.3% (3e814130) down to 3.3% (76b2941d) |
| app_category (app rows) | from 25.0% (f95efa07) down to 9.0% (8ded1f7a) |
| banner_pos | position 0 16.5% , position 1 18.4% |
| hour / weekday | CTR only 16% to 19% , though traffic runs from 2% to 6% of rows across hours |

- **How columns go together :** correlation on the codes only reflects how the labels are numbered (C14 , C15 read 0.00 though C14 fixes C15). Cramér's V , written from scratch in `self_module/stats.py` , uses the chi-squared statistic of the crosstab : 0 means unrelated , 1 means one column fixes the other. V = 1 for C14 with C15 , C16 , C17 and C21 , for C17 with C21 and for app_id with app_domain. C1 and device_type are close (0.82) but not one to one. No device_type code is defined anywhere , so we don't name them.

## 3. Machine learning

- **Feature engineering :** `hour` becomes hour of day and weekday.
- **Feature selection :** cost is how much validation log loss rises without the column ([table in results.md](results.md)).
  - `id` : a row key.
  - `device_id` , `device_ip` : hundreds of thousands of values that identify users , not kinds of impressions.
  - `C1` : saves 5 columns , costs 0.00001.
  - `C14` : saves 421 columns , costs 0.00094 , and the model doesn't fit in the GPU with it.
  - `C18` , `C19` , `C21` : C17 fixes or almost fixes them. Saves 108 columns , costs 0.00013 , and makes room for 1 in 40.
  - `app_domain` : fixed by app_id. Saves 24 columns , costs 0.00006.
- **Rare values :** any value in fewer than 0.025% of train rows becomes `other`. One hot encoding then gives 1,356 columns , all standardised with train statistics only. At 0.1% , 30% of device_model rows land in other , at 0.025% only 13% , and log loss falls by 0.0043 at 1 in 32.
- **More rows alone barely help :** at the 0.1% cut , 1 in 128 to 1 in 32 gains 0.0010 and 1 in 20 gains nothing more. So the sample stayed at what fits and the columns got the room.
- **Leakage :** the kept values , the one hot columns and the scaler all come from train. Valid is used for the threshold , for C and for the settings above. Test is used once.
- **Models :**
  - a baseline that always predicts the train CTR
  - logistic regression
  - class weighted logistic regression (each class carries half the loss)
  - class weighted linear SVM , with C tuned on validation

  All three fitted models use full batch gradient descent on the GPU.

**Test results** (101,073 impressions , threshold for precision / recall / F1 picked by best F1 on validation) :

| model | log loss | ROC-AUC | PR-AUC | precision | recall | F1 |
|---|---|---|---|---|---|---|
| baseline (always the train CTR) | 0.458 | 0.500 | 0.171 | - | 0 | 0 |
| **logistic regression** | **0.405** | **0.734** | **0.358** | 0.291 | 0.683 | 0.408 |
| logistic regression , class weighted | 0.603 | 0.734 | 0.357 | 0.293 | 0.666 | 0.407 |
| linear SVM , class weighted (C = 0.01) | - | 0.717 | 0.312 | 0.277 | 0.693 | 0.396 |

The SVM gives a score , not a probability , so it has no log loss. Plain logistic matches sklearn's `LogisticRegression` to 3 decimals. The SVM is close to sklearn's `SGDClassifier` on ranking (ROC-AUC 0.717 against 0.713 , PR-AUC 0.312 for both) and on F1 (0.396 against 0.394).

## 4. Inference and interpretation

- **Performance :** plain logistic regression is the best model. Its log loss is 0.405 against 0.458 for the baseline (12% lower) , ROC-AUC 0.734 and PR-AUC 0.358 (the base rate is 0.171). Train and test agree , so it is not overfitting , and our model matches sklearn's to 3 decimals.
- **Ranking :** the 10% of test impressions the model rates highest are clicked 41% of the time , the lowest 10% only 1.8% of the time. That is a 23x gap.
- **Calibration :** the plain model's probabilities follow the real CTR across the deciles (it says 43% , reality is 41%). Class weighting does not rank any better (ROC-AUC 0.734) and pushes every probability up (mean 0.44 against a real 0.17) , which is why its log loss is 0.603. Taking log(c_pos / c_neg) off the bias undoes it (log loss back to 0.405 , almost the same as the plain model). For an ad platform the probability goes straight into the bid , so calibration matters more than any threshold.
- **SVM :** it ranks worse than logistic regression and gives a score instead of a probability , so it can't price an impression.
- **Important features :** site and app categories , specific sites and apps , banner position 1 , and some C17 values. Many one hot columns overlap (a site sits inside a category) , so a weight is the effect with the other columns held fixed , not the raw CTR gap.
- **Predictive vs causal :** websites click more than apps , and position 1 more than position 0 , but ads are not placed at random. Advertisers , publishers and the platform choose where each ad goes and who sees it , so a high CTR in position 1 may just mean better ads get position 1. The model finds which impressions tend to get clicked. Whether moving an ad changes its clicks needs an experiment (an A/B test that randomises the placement).
- **Limitations :**
  - 1 in 40 rows used.
  - Rare values merged into `other`.
  - The features are hashed and anonymised , so they are hard to explain to the business.
  - Only 10 days. The given split is random , so test comes from the same days as train , and new days will probably score a bit worse.
  - A linear model misses combinations (this app on this device).
  - No user history , since device_id and device_ip were dropped.

## 5. Recommendations

1. **Score every impression with the plain logistic model and bid by expected value** , P(click) x price per click. Its probabilities are calibrated , so they can be used directly.
2. **Put the budget on the top of the ranking.** The top 30% by predicted probability click at about 32% , the bottom 30% at about 4.5%.
3. **Shift spend between segments , but test it first.**
   - Website inventory (20% CTR) beats in-app (12%).
   - Connection type 0 and device type 0 beat the rest.
   - Connection types 3 / 5 , device types 4 / 5 and the weakest site categories (f66779e6 , 76b2941d , below 4%) are the first places to cut.

   These are associations , so move a small share of budget in an A/B test before moving the rest.
4. **Don't bid with a class weighted model.** If weights are used for a yes / no rule , take log(c_pos / c_neg) off the bias first.
5. **Next steps :**
   - Train on all 40 million rows , with batching.
   - Add models that learn combinations of features (factorisation machine , neural network , boosting).
   - Add user-history features (how often a device_ip / device_id appears) , computed on train only.
   - Validate on the last day instead of a random split.
