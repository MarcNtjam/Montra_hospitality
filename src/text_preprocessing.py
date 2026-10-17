"""
Montra Guest Experience Analytics — NLP preprocessing pipeline.

One standardised, importable workflow for preparing guest review text, so the
notebook, the experiments and any future scoring job all clean text the same way.

Three preprocessing levels are exposed because they are compared as an experiment:

    minimal     unicode normalisation, lowercasing, whitespace collapse
    standard    minimal + contraction expansion (keeps negation as "not"),
                punctuation/digit removal                       <- default
    aggressive  standard + English stop-word removal (which also deletes
                negation words such as "not", "no", "never")

Sentence splitting and connector stripping support sentence-level topic modelling,
because a single review usually covers two or three different aspects of a stay.
"""
from __future__ import annotations

import re
import unicodedata

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Contractions are expanded so that negation survives as an explicit token ("not").
_CONTRACTIONS = [
    (r"\bwon't\b", "will not"),
    (r"\bcan't\b", "cannot"),
    (r"\bshan't\b", "shall not"),
    (r"n't\b", " not"),
    (r"'re\b", " are"),
    (r"'ll\b", " will"),
    (r"'ve\b", " have"),
    (r"'m\b", " am"),
    (r"'d\b", " would"),
    (r"'s\b", ""),          # possessive / "it's" -> dropped (low information)
]

# Discourse connectors that open sentences ("On top of that, ...").
# They carry no topic, so they are removed before topic modelling.
CONNECTORS = [
    "on top of that", "in addition", "on the other hand", "that said", "meanwhile",
    "plus", "also", "however", "honestly", "overall", "unfortunately", "sadly",
    "additionally", "besides", "still", "although", "but",
]
_CONNECTOR_RE = re.compile(
    r"^\s*(?:(?:" + "|".join(re.escape(c) for c in CONNECTORS) + r")\s*,?\s*)+",
    flags=re.IGNORECASE,
)

# Stop words used for the "aggressive" strategy. Note: this list contains
# "not", "no", "nor", "never" — removing them is exactly what the experiment tests.
STOP_WORDS = set(ENGLISH_STOP_WORDS)
NEGATIONS = {"not", "no", "nor", "never", "cannot", "without"}

LEVELS = ("minimal", "standard", "aggressive")


def normalise_unicode(text: str) -> str:
    """NFKC-normalise and replace typographic dashes/quotes with plain ASCII."""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.replace("—", " - ").replace("–", " - ")
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def expand_contractions(text: str) -> str:
    for pattern, repl in _CONTRACTIONS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def clean_text(text: str, level: str = "standard") -> str:
    """Clean one review at the requested preprocessing level."""
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}")
    text = normalise_unicode(text).lower()
    if level == "minimal":
        return re.sub(r"\s+", " ", text).strip()

    text = expand_contractions(text)
    text = re.sub(r"[^a-z\s]", " ", text)          # drop punctuation and digits
    tokens = text.split()
    if level == "aggressive":
        tokens = [t for t in tokens if t not in STOP_WORDS]
    return " ".join(tokens)


def split_sentences(text: str) -> list[str]:
    """Split a review into sentences (each usually describes one aspect)."""
    text = normalise_unicode(text)
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 3]


def strip_connectors(sentence: str) -> str:
    """Remove leading discourse connectors: 'On top of that, the pool...' -> 'the pool...'."""
    return _CONNECTOR_RE.sub("", sentence).strip()


def preprocess_corpus(texts, level: str = "standard") -> list[str]:
    """Vectorisable convenience wrapper used across the notebook."""
    return [clean_text(t, level) for t in texts]


# ---------------------------------------------------------------------------
# scikit-learn compatible step, so the same cleaning is baked into saved models
# ---------------------------------------------------------------------------
from sklearn.base import BaseEstimator, TransformerMixin


class TextPreprocessor(BaseEstimator, TransformerMixin):
    """Pipeline step: Pipeline([("prep", TextPreprocessor("standard")), ("tfidf", ...), ("clf", ...)]).
    Makes a saved model accept raw review text and apply the identical preprocessing."""

    def __init__(self, level: str = "standard"):
        self.level = level

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return preprocess_corpus(X, self.level)
