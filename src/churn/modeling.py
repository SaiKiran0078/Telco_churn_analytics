"""Train/test split and candidate models."""
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .config import RANDOM_STATE
from .features import CATEGORICAL, NUMERIC, add_features, build_preprocessor

FEATURES = NUMERIC + CATEGORICAL


def load_xy(path):
    df = add_features(pd.read_csv(path))
    return df, df[FEATURES], df["ChurnFlag"]


def split(X, y):
    """80/20 stratified split. The test set is touched once, at the very end."""
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)


def candidates():
    return {
        "Baseline (predict base rate)": Pipeline([("prep", build_preprocessor()), ("m", DummyClassifier(strategy="prior"))]),
        "Logistic regression": Pipeline([("prep", build_preprocessor()), ("m", LogisticRegression(C=0.5, max_iter=2000))]),
        "Random forest": Pipeline([("prep", build_preprocessor(scale=False)),
                                   ("m", RandomForestClassifier(n_estimators=400, min_samples_leaf=5, n_jobs=2, random_state=RANDOM_STATE))]),
        "Gradient boosting": Pipeline([("prep", build_preprocessor(scale=False)),
                                       ("m", HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=250, random_state=RANDOM_STATE))]),
    }
