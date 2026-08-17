"""Bitemporal NLP evaluation with an intentionally leaky comparator."""

from .data import NewsCorpus, generate_corpus, temporal_split
from .experiment import run_experiment
from .features import build_documents
from .models import CalibratedTextClassifier

__all__ = ["CalibratedTextClassifier", "NewsCorpus", "build_documents", "generate_corpus", "run_experiment", "temporal_split"]
