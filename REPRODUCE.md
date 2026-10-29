# Reproduce

## Environment

Python 3.11.

```bash
pip install -r requirements.txt
```

A CUDA GPU is optional. The part 1 model notebooks put the data on the GPU when there is one (about 3.5 GB of GPU memory) and run on the CPU otherwise , only slower.

## Data

`data/` is git-ignored , so it starts empty.

| part | file | how to get it |
|---|---|---|
| 1 | `data/Dataset1.zip` (1.3 GB , the Avazu click logs) | download from the [Google Drive link in the brief](https://drive.google.com/file/d/1vNLFrCZR0lVix4E_77QxL7ORd931FTPi/view?usp=sharing) and put it in `data/` , don't unzip it |
| 2 | `data/jtpa_india_synthetic_40000.csv` | downloaded by `01_data_and_randomisation.ipynb` from [GitHub](https://raw.githubusercontent.com/hirdeshiitkgp/Data/refs/heads/main/jtpa_india_synthetic_40000.csv) |

Everything else in `data/` is written by the notebooks.

## Run order

Open each notebook from its own folder (Jupyter's default) and run them in numbered order.

**Part 1 , `projects/ctr_competition/`**

| notebook | writes | time |
|---|---|---|
| `01_eda.ipynb` | `data/ctr/*_sample.parquet` (every 32nd row of each split) , `data/ctr/sizes.csv` | ~1.5 min the first time , seconds after |
| `02_data_prep.ipynb` | `data/ctr/X_*.parquet` , `data/ctr/y_*.parquet` (needs ~14 GB RAM) | ~20 s |
| `03_logistic_regression.ipynb` | `data/ctr/logistic_test.parquet` | ~6 min on GPU |
| `04_svm.ipynb` | | ~7 min on GPU |

**Part 2 , `projects/job_training_causal_inference/`**

| notebook | time |
|---|---|
| `01_data_and_randomisation.ipynb` | seconds |
| `02_itt.ipynb` | seconds |

Headless , from the notebook's folder :

```bash
jupyter nbconvert --to notebook --execute --inplace 01_eda.ipynb
```

Times are from a laptop with an RTX 3050 (6 GB) and 32 GB RAM. The sample is fixed rows (every 32nd) and the models start from zero weights , so reruns give the same numbers (up to tiny GPU rounding).
