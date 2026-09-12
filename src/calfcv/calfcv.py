import time
from scipy.sparse import issparse
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.multiclass import unique_labels, type_of_target
from sklearn.utils.validation import check_is_fitted
from .calf import Calf

try:
    from sklearn.utils.validation import validate_data

    HAS_VALIDATE_DATA = True
except ImportError:
    HAS_VALIDATE_DATA = False


class CalfCV(ClassifierMixin, TransformerMixin, BaseEstimator):
    """Course approximation linear function with cross validation"""

    def __init__(self, grid=(-1, 1), auc_tol=1e-6, order_col=False, verbose=False):
        self.grid = [grid] if isinstance(grid, int) else grid
        self.auc_tol = auc_tol
        self.order_col = order_col
        self.verbose = verbose

    def fit(self, X, y):
        if y is None:
            raise ValueError("requires y to be passed, but the target y is None")

        # Fix 1: Handle unknown object dtypes cleanly
        y_type = type_of_target(y)
        if y_type == "unknown":
            raise ValueError("Unknown label type: target y must be binary.")
        if y_type != "binary":
            raise ValueError(
                f"Only binary classification is supported. The type of the target is {y_type}."
            )

        if HAS_VALIDATE_DATA:
            X, y = validate_data(
                self, X=X, y=y, accept_sparse=["csr", "csc", "coo"], reset=True
            )
        else:
            X, y = self._validate_data(
                X=X, y=y, accept_sparse=["csr", "csc", "coo"], reset=True
            )

        self.X_ = X
        self.y_ = y
        self.classes_ = unique_labels(y)

        parameter_grid = {
            "classifier__grid": [self.grid],
            "classifier__auc_tol": [self.auc_tol],
            "classifier__order_col": [self.order_col],
            "classifier__verbose": [self.verbose],
        }

        steps = [("classifier", Calf())]
        if not issparse(X):
            steps.insert(0, ("scaler", StandardScaler()))

        self.model_ = GridSearchCV(
            estimator=Pipeline(steps=steps),
            param_grid=parameter_grid,
            scoring="roc_auc",
            verbose=self.verbose,
        )

        start = time.time()
        self.model_.fit(X, y)
        self.fit_time_ = time.time() - start

        self.best_score_ = self.model_.best_score_
        self.best_coef_ = self.model_.best_estimator_["classifier"].coef_
        self.best_auc_ = self.model_.best_estimator_["classifier"].auc_

        return self

    def decision_function(self, X):
        check_is_fitted(self)
        return self.model_.decision_function(X)

    def predict(self, X):
        check_is_fitted(self)
        return self.model_.predict(X)

    def predict_proba(self, X):
        check_is_fitted(self)
        return self.model_.predict_proba(X)

    def transform(self, X):
        check_is_fitted(self)
        return self.model_.transform(X)

    def fit_transform(self, X, y):
        return self.fit(X, y).model_.transform(X)

    def _more_tags(self):
        return {"poor_score": True, "non_deterministic": True, "binary_only": True}

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.classifier_tags.poor_score = True
        tags.classifier_tags.multi_class = False
        tags.input_tags.sparse = True
        tags.non_deterministic = True
        tags.estimator_type = "classifier"
        return tags
