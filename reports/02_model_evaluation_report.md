# Model Evaluation Report — Montra Guest Experience Analytics

**Phases 5–8 · Objectives 4, 6 and 7** · Source: `notebook/guest_experience_analysis.ipynb`, sections 4.4–4.6 and 6.1–7.6 · Experiments: MLflow (`mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db`)

## 1. Evaluation set-up

| Item | Choice |
|---|---|
| Modelling corpus | 34,460 reviews (35,000 minus duplicate texts and 196 reviews whose identical text carries conflicting labels) |
| Split | Stratified 70 / 15 / 15: train 24,122, validation 5,169, test 5,169. Zero text overlap between splits |
| Classes | negative 28.2%, neutral 37.9%, positive 33.9% |
| Primary metric | **Macro-F1**, so the smallest class counts equally. Accuracy, precision and recall also reported |
| Model comparison | Validation set. 5-fold cross-validation for the grid and tuning |
| Final check | Held-out test set, used once for the selected model |
| Selection rule | Best validation macro-F1; any model within 0.003 of it (run-to-run noise) is a tie, and the simplest tied model wins |

## 2. Sentiment classification results

### Baselines vs the BERT-family model (validation)

| Model | Macro-F1 | Accuracy | Neutral F1 | Training time |
|---|---|---|---|---|
| **RoBERTa-base, fine-tuned** (6,000 reviews, 64 tokens, 3 epochs) | **0.943** | 0.942 | **0.926** | 57.5 min (CPU) |
| Random Forest (TF-IDF word unigrams) | 0.942 | 0.941 | 0.924 | 30 s |
| Logistic Regression (TF-IDF) | 0.940 | 0.939 | 0.922 | 1 s |
| Linear SVM (TF-IDF) | 0.939 | 0.937 | 0.920 | 1 s |
| RoBERTa-base, 32 tokens, 2 epochs | 0.939 | 0.938 | 0.921 | 24 min |
| Multinomial Naive Bayes | 0.928 | 0.926 | 0.907 | < 1 s |

- **All strong models are statistically tied** (0.940–0.943). Naive Bayes trails by about 0.01.
- **RoBERTa is the most data-efficient.** Trained on a quarter of the data, it matches models trained on all 24,122 reviews, and it has the best neutral F1.
- **Neutral is the hardest class for every model.** Errors flow between neutral and its neighbours, almost never between positive and negative.

### Experiments (Objective 7)

| Experiment | Runs | Finding |
|---|---|---|
| Preprocessing (minimal / standard / aggressive) × features (word 1-gram, word 1–2-gram, char 2–5-gram) × model (LR, SVM, NB) | 27 | Preprocessing spread 0.0006 and feature spread 0.0015 macro-F1. Model family matters most. The top eight configurations are within one cross-validation standard deviation |
| Hyperparameter tuning (C for LR and SVM, α for NB) | 19 | LR best at C = 4 (0.9416 CV), SVM at C = 1 (0.9412). NB gains most (+0.004) but still trails. Tuning adds ≤ 0.002 for LR and SVM |
| Sequence length | 2 | 32 tokens truncates 74.7% of reviews and scores 0.939; 64 tokens truncates none and scores 0.943 |
| Epochs | per-epoch log | Validation macro-F1 0.941 → 0.943 → 0.943. Two epochs are enough |

All 52 sentiment runs are in the MLflow experiment `montra-sentiment`.

### Final model and test performance

- **Best validation score:** RoBERTa-base, 0.9434. **Random Forest (0.9422) is within the 0.003 tolerance**, so the parsimony rule selects **Random Forest**. Tuned Logistic Regression (0.9403) misses the tolerance by 0.0001 and is an equally reasonable choice: about 350× smaller and interpretable.
- **Held-out test set (Random Forest):**

| Class | Precision | Recall | F1 |
|---|---|---|---|
| negative | 0.963 | 0.934 | 0.948 |
| neutral | 0.904 | 0.945 | 0.924 |
| positive | 0.967 | 0.942 | 0.955 |
| **macro average** | 0.945 | 0.940 | **0.942** |

Accuracy 0.941. RoBERTa-base scores 0.943 macro-F1 on the same test set, confirming the validation tie. When unsure, the model leans towards *neutral* (recall 0.945, precision 0.904), which is the conservative choice. The model is registered in the MLflow Model Registry as `montra-sentiment-classifier`, and its run ID is stamped on every prediction.

## 3. Error analysis

**Test error rate: 5.90%** (305 of 5,169 reviews).

| Pattern | Share of test reviews | Error rate in group | Outside group | Lift |
|---|---|---|---|---|
| Label disagrees with rating (likely label noise) | 5.2% | 100% | 0.7% | 16.9× |
| Hedged or ambiguous language (*fine, adequate, as expected*) | 46.0% | 8.1% | 4.0% | 1.4× |
| Contrast connector (*but, however, that said*) | 35.4% | 7.2% | 5.2% | 1.2× |
| Negation (*not, no, never*) | 24.8% | 5.9% | 5.9% | 1.0× |
| Multiple topics (3+ aspects) | 6.9% | 5.8% | 5.9% | 1.0× |
| Mixed sentiment (polar + neutral sentences) | 16.5% | 4.4% | 6.2% | 0.8× |

- **Label noise explains almost everything.** 88.9% of errors come from reviews whose label contradicts their rating band. Where label and rating agree, the model is **99.3% accurate**. In the contradicting cases the model sides with the text and the rating; for example, a review rated 3.5 and labelled *neutral* that says *"the pricing exceeded our expectations — excellent value"* is predicted *positive*.
- **Hedging is the only real linguistic difficulty.** Negation and multi-topic reviews cause no extra errors; one strongly worded sentence makes mixed polar-plus-neutral reviews easier.
- **Confusions:** every error but one crosses the neutral boundary; exactly one positive review was predicted negative.
- **Untested:** no review mixes a positive and a negative sentence, so true mixed sentiment could not be evaluated.

## 4. Topic modelling evaluation (Objective 4)

Six BERTopic configurations on the 6,575 unique review sentences, all logged to MLflow (`montra-topic-modelling`). Sentence vectors come from RoBERTa-base (hidden layers 4–8, "all-but-the-top" post-processing).

| Config | Sentence vector | Min cluster size | Topics | Outliers | NPMI | Diversity | Aspect purity | Sentiment leakage | Score |
|---|---|---|---|---|---|---|---|---|---|
| A | all tokens | 80 | 39 | 18.0% | 0.081 | 0.74 | 0.83 | 0.451 | 1.197 |
| B | aspect tokens | 40 | 67 | 11.9% | 0.075 | 0.41 | 0.91 | 0.139 | 1.253 |
| C | aspect tokens | 80 | 39 | 15.7% | 0.072 | 0.63 | 0.92 | 0.075 | 1.549 |
| D | aspect tokens | 120 | 21 | 25.2% | −0.181 | 0.69 | 0.83 | 0.059 | 1.280 |
| **E** | **aspect tokens, merged to 30** | **80** | **29** | **15.7%** | **0.031** | **0.71** | **0.90** | **0.057** | **1.583** |
| F | TF-IDF benchmark (not selectable) | 3 strings | 22 | 0.2% | 0.005 | 0.90 | 0.87 | 0.011 | 1.763 |

Score = coherence + diversity + aspect purity − sentiment leakage, among configurations with at most 35% outliers.

- **Averaging over all tokens (A) clusters by mood**, not subject (leakage 0.451). Averaging over the aspect words only cuts leakage to 0.06–0.14.
- **E is selected.** After outlier reduction (validated: every re-assigned sentence matched its own aspect words), 10% of aspect-bearing sentences remain outliers and fall back to the aspect lexicon.
- **Aspect assignment:** BERTopic's topic aspect is kept for 57.7% of all sentences, corrected by sentence-level reconciliation for 5.8%, and taken from the lexicon for 7.1% (outliers). The remaining 29.4% are overall-impression statements with no aspect.
- **TF-IDF scores higher on word-based metrics, as expected**, because those metrics are computed from the same word counts. It is kept as a reference only.

## 5. Conclusions

1. **Recommended model:** Random Forest or Logistic Regression for this dataset. Same accuracy as the transformer, trained in seconds. The fine-tuned RoBERTa-base is the best and most data-efficient model, and the better choice once review text becomes more varied.
2. **The ceiling is the labels, not the model.** Re-checking the ~5% of reviews whose label contradicts the rating would raise measured accuracy towards 99%.
3. **Topic models need guiding.** Aspect-focused embeddings and a sentence-level validation step turned BERTopic's clusters into reliable business aspects.

## 6. Notes on the reference execution

- Hugging Face was unreachable in the reference execution. RoBERTa-base weights were loaded from spaCy's `en_core_web_trf` GitHub release, converted to Hugging Face format (same architecture and vocabulary, additionally trained by spaCy on English tagging and parsing). With internet access, the notebook downloads the original `roberta-base` and uses `all-MiniLM-L6-v2` for topic embeddings.
- The RoBERTa results are stored in `data/processed/bert_results.json` and the topic embeddings in `data/processed/sentence_embeddings.npz`, so a re-run reproduces them without retraining. Set `RUN_BERT = True` to retrain.
