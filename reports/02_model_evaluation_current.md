# Current model evaluation report

Selected model: **Logistic Regression (tuned: standard, char_2-5gram, C=8)**. Selection uses validation macro-F1 and a 0.003 parsimony tolerance.

| model                                                     | family              |   complexity |   val_accuracy |   val_precision_macro |   val_recall_macro |   val_f1_macro |   val_f1_negative |   val_f1_neutral |   val_f1_positive |   test_accuracy |   test_precision_macro |   test_recall_macro |   test_f1_macro |   test_f1_negative |   test_f1_neutral |   test_f1_positive |
|:----------------------------------------------------------|:--------------------|-------------:|---------------:|----------------------:|-------------------:|---------------:|------------------:|-----------------:|------------------:|----------------:|-----------------------:|--------------------:|----------------:|-------------------:|------------------:|-------------------:|
| RoBERTa-base (bert_len64_ep3)                             | Transformer         |            4 |       0.942155 |              0.946232 |           0.941251 |       0.943389 |          0.947993 |         0.925603 |          0.956572 |        0.941962 |               0.945751 |            0.941353 |        0.943264 |           0.949164 |          0.925187 |           0.95544  |
| Random Forest (baseline: standard, word_1gram)            | Random Forest       |            3 |       0.940801 |              0.945015 |           0.939845 |       0.942056 |          0.94656  |         0.923918 |          0.955691 |        0.940801 |               0.944518 |            0.940233 |        0.942096 |           0.947808 |          0.923921 |           0.954559 |
| Logistic Regression (tuned: standard, char_2-5gram, C=8)  | Logistic Regression |            2 |       0.93964  |              0.944356 |           0.938679 |       0.94106  |          0.947589 |         0.922657 |          0.952934 |        0.938866 |               0.943351 |            0.937943 |        0.940234 |           0.945861 |          0.921549 |           0.953293 |
| Linear SVM (tuned: standard, char_2-5gram, C=3)           | Linear SVM          |            2 |       0.938286 |              0.943298 |           0.937155 |       0.939711 |          0.945747 |         0.921059 |          0.952326 |        0.939834 |               0.944116 |            0.939047 |        0.941207 |           0.947332 |          0.922695 |           0.953596 |
| Naive Bayes (tuned: aggressive, word_1-2gram, alpha=0.01) | Naive Bayes         |            1 |       0.931708 |              0.938324 |           0.929899 |       0.933249 |          0.938315 |         0.913417 |          0.948014 |        0.934997 |               0.940344 |            0.933867 |        0.936535 |           0.943277 |          0.916996 |           0.94933  |

## Error analysis

| pattern                                        |   share of test reviews |   error rate in group |   error rate outside group |   share of all errors |   lift vs overall |
|:-----------------------------------------------|------------------------:|----------------------:|---------------------------:|----------------------:|------------------:|
| Label disagrees with rating (audit flag)       |               0.0524279 |             0.99631   |                 0.00939159 |             0.85443   |         16.2972   |
| Hedged / ambiguous language                    |               0.46005   |             0.0849453 |                 0.0408456  |             0.639241  |          1.3895   |
| Contrast connector (but / however / that said) |               0.354421  |             0.0764192 |                 0.052742   |             0.443038  |          1.25003  |
| Multiple topics (3+ aspects)                   |               0.0367576 |             0.0631579 |                 0.0610564  |             0.0379747 |          1.03311  |
| Negation (not / no / never / n't)              |               0.24821   |             0.0600156 |                 0.0615028  |             0.243671  |          0.981711 |
| Mixed sentiment (polar + neutral sentences)    |               0.159992  |             0.0580411 |                 0.0617227  |             0.151899  |          0.949413 |

Rating disagreements require manual review; they do not by themselves prove label noise. The candidate test scores are descriptive after validation selection; do not tune using them.
