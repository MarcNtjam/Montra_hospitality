# Running the three Montra notebooks

Run from the project root or notebook folder in VS Code. Select the same Python environment for each notebook. Save your existing project first, then copy this package over it. Your existing .env and .git folder are not included and should stay in your original project. This package does include the supplied guest data for local execution; the data/ folder remains ignored by Git.

The shared text helper now transliterates accented letters during standard cleaning (for example, décor → decor), matching the supplied reference training corpus. This correction can change topic embedding cache keys.

Experiments default to one worker to keep memory use predictable. Set the MONTRA_N_JOBS environment variable to increase parallelism.

Install requirements in your environment:

    python -m pip install -r requirements.txt

## Run order

1. notebook/cleaning_eda.ipynb: data collection, checks, cleaning, EDA and every existing explanation. USE_DATABASE=False uses the supplied raw snapshots. The final cell exports reviews_clean.csv and nlp_corpus.csv.
2. Restart the kernel. Run notebook/bert.ipynb: Phases 5–7, BERTopic, aspect sentiment, baselines and BERT-family (RoBERTa-base) classification. The final cell saves models/phase7_handoff.joblib.
3. Restart the kernel. Run notebook/machine_learning_and_analytics.ipynb: Phases 8–9, experiment grid, tuning, evaluation, error analysis, guest analytics and the complete original business report and conclusion. The last cell exports updated tables and current Markdown reports.

Each notebook loads its own prerequisites from disk. They do not require another notebook's active kernel. If upstream data changes, rerun the downstream notebooks. The final analytics notebook requires the Phase 7 checkpoint; it intentionally stops with instructions when it is missing.

## Preserved work

The initial combined notebook and earlier notebooks remain available under notebook/reference/. All original Phase 5–9 code sections, charts and interpretation paragraphs are retained in the new workflow. Original numerical insight paragraphs are labelled as reference findings. Newly generated results can differ with package versions, embedding backend, training configuration or inputs. Reports ending in _current.md are generated from the current execution; original reports retain their original findings.

The cleaning notebook retains Unknown for missing loyalty rather than assuming it means no membership. Original NLP training corpus deduplication uses exact original review text to preserve its split IDs. The additional cleaned-text deduplication export in cleaning_eda remains available separately.

## BERT and cached results

The original model is RoBERTa-base, a BERT-family transformer, not the exact bert-base model. Both classical and transformer models remain included so their performance can be compared.

RUN_BERT='auto' reuses the supplied bert_results.json after checking data identity and exact ordered split IDs. Those cached predictions reproduce reference validation comparisons; they are not saved model weights and are not a new training run. Set RUN_BERT=True in bert.ipynb to train afresh and write weights/tokenizer into models/bert_sentiment/. This needs PyTorch, Transformers and access to the pretrained weights (or MONTRA_TRANSFORMER pointing to local weights). Original CPU training uses a balanced subset of 6,000 reviews and can take about an hour; additional experiments take more time.

The embedding cache is included. Cache misses may download a pretrained embedding model; the original TF-IDF/SVD fallback remains available and can change topic results. The transformer may win model selection; if only cached predictions exist and its weights are missing, the analytics notebook stops explicitly rather than inventing all-review predictions. Train/save the model first in that case.

## What models and mlruns contain

models/ stores fitted reusable objects. It was empty in the uploaded ZIP. The Phase 7 handoff includes fitted classical baselines, split data, sentence scores and a lightweight topic-word lookup. Phase 8 saves sentiment_classifier_final.joblib for a selected classical model. Transformer weights are saved only when actual fine-tuning runs.

mlruns/ stores experiment tracking, created by MLflow at execution time. It was empty in the uploaded ZIP. These notebooks use mlruns/mlflow.db for parameters, metrics and run metadata; artifacts are under mlruns/artifacts/. A CSV or JSON of old predictions does not recreate the original MLflow database. Reference BERT runs are clearly tagged when logged from cache.

To open the experiment UI from the project root:

    mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db

## Interpretation limits retained alongside the findings

- Review labels are supplied data, and their provenance needs confirmation.
- Rating-band disagreement is an audit flag, not proof that a sentiment label is wrong.
- The sentence scorer is trained on review-level labels. Aspect sentiment is exploratory and has no independently annotated sentence-level test set.
- The rating regression is an in-sample association, not a causal or independently validated effect.
- Model selection uses validation scores. Candidate test scores are descriptive after that selection and must not be used to tune the model.
- Portfolio predictions include reviews used in model training; use held-out test metrics for generalisation claims.

## GitHub

Save notebooks, review git status, then commit and push code changes. data/, models/ and mlruns/ remain local, so this is not a full data/model backup. The distributed archive excludes .env, Git history, Python caches and the database-URL document. Keep database credentials out of notebook cells/outputs and public reports.

The downloadable package contains inputs and source code, not the fitted objects or MLflow history created during verification. Those folders populate when you run your notebooks.
