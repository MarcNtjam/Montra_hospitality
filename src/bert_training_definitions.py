def bert_ready():
    try:
        import torch, transformers  # noqa
        return True
    except ImportError as e:
        print("BERT skipped: missing library →", e.name, "(pip install torch transformers accelerate)")
        return False

def train_bert(max_len=64, epochs=3, lr=3e-5, batch_size=16, run_name=None, save=True):
    import torch, inspect
    from transformers import (AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments,
                              Trainer, DataCollatorWithPadding, TrainerCallback, set_seed)
    set_seed(SEED)
    on_gpu = torch.cuda.is_available()
    tr = train_df
    if not on_gpu and BERT_TRAIN_LIMIT and len(train_df) > BERT_TRAIN_LIMIT:
        tr = train_df.groupby("sentiment_label").sample(n=BERT_TRAIN_LIMIT // 3, random_state=SEED)
    tok = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)

    class ReviewDS(torch.utils.data.Dataset):
        def __init__(self, frame):
            self.enc = tok([normalise_unicode(t) for t in frame["review_text"]], truncation=True, max_length=max_len)
            self.y = frame["sentiment_label"].map(LABEL2ID).tolist()
        def __len__(self): return len(self.y)
        def __getitem__(self, i):
            item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
            item["labels"] = torch.tensor(self.y[i]); return item

    ds_tr, ds_val, ds_te = ReviewDS(tr), ReviewDS(val_df), ReviewDS(test_df)
    model = AutoModelForSequenceClassification.from_pretrained(
        BERT_MODEL_NAME, num_labels=3, id2label={i: l for l, i in LABEL2ID.items()}, label2id=LABEL2ID)

    def compute_metrics(p):
        preds = np.argmax(p.predictions, axis=1)
        return {k.replace("val_", ""): v for k, v in eval_metrics(
            [SENT_ORDER[i] for i in p.label_ids], [SENT_ORDER[i] for i in preds], "val_").items()}

    class MlflowEpochLogger(TrainerCallback):
        def on_evaluate(self, args, state, control, metrics=None, **kw):
            if metrics:
                mlflow.log_metrics({k.replace("eval_", "val_"): v for k, v in metrics.items()
                                    if isinstance(v, (int, float))}, step=int(round(state.epoch or 0)))

    ta = dict(output_dir=str(MODEL_DIR / "bert_checkpoints" / (run_name or "run")), num_train_epochs=epochs,
              per_device_train_batch_size=batch_size, per_device_eval_batch_size=128, learning_rate=lr,
              weight_decay=0.01, warmup_ratio=0.1, save_strategy="no", logging_strategy="epoch",
              report_to="none", seed=SEED, disable_tqdm=False)
    # keep the cell working across transformers 4.x and 5.x (argument names changed between versions)
    accepted = set(inspect.signature(TrainingArguments.__init__).parameters)
    ta["eval_strategy" if "eval_strategy" in accepted else "evaluation_strategy"] = "epoch"
    if "warmup_ratio" not in accepted:
        ta["warmup_steps"] = ta.pop("warmup_ratio")      # v5: a float < 1 is read as a ratio
    ta = {k: v for k, v in ta.items() if k in accepted}
    trainer = Trainer(model=model, args=TrainingArguments(**ta), train_dataset=ds_tr, eval_dataset=ds_val,
                      data_collator=DataCollatorWithPadding(tok), compute_metrics=compute_metrics,
                      callbacks=[MlflowEpochLogger()])
    run_name = run_name or f"bert_len{max_len}_ep{epochs}"
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags({"stage": "bert", "model_family": "transformer"})
        mlflow.log_params({"model": BERT_LABEL, "max_len": max_len, "epochs": epochs, "learning_rate": lr,
                           "batch_size": batch_size, "train_rows": len(tr), "device": "cuda" if on_gpu else "cpu",
                           "preprocessing": "raw text (subword tokeniser)"})
        t0 = time.time(); trainer.train(); secs = time.time() - t0
        val_pred = [SENT_ORDER[i] for i in np.argmax(trainer.predict(ds_val).predictions, axis=1)]
        test_pred = [SENT_ORDER[i] for i in np.argmax(trainer.predict(ds_te).predictions, axis=1)]
        mv = eval_metrics(val_df["sentiment_label"], val_pred, "val_")
        mlflow.log_metrics({**mv, "train_seconds": secs})
        hist = [{"epoch": int(round(h["epoch"])), "val_f1_macro": h["eval_f1_macro"], "val_accuracy": h["eval_accuracy"]}
                for h in trainer.state.log_history if "eval_f1_macro" in h]
        if save:
            trainer.save_model(str(BERT_SAVE_DIR)); tok.save_pretrained(str(BERT_SAVE_DIR))
            mlflow.set_tag("model_path", str(BERT_SAVE_DIR.relative_to(PROJECT_ROOT)))
    return {"run": run_name, "max_len": max_len, "epochs": epochs, "train_rows": len(tr), "train_seconds": secs,
            **mv, "epoch_history": hist, "val_pred": val_pred, "test_pred": test_pred}
