import time
import numpy as np
from scipy.sparse import issparse, csr_array
from scipy.special import expit
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.preprocessing import minmax_scale
from sklearn.utils.multiclass import unique_labels, type_of_target
from sklearn.utils.validation import check_is_fitted
from ._utils import predict, fit_hv, fit_hv_sparse

try:
    from sklearn.utils.validation import validate_data

    HAS_VALIDATE_DATA = True
except ImportError:
    HAS_VALIDATE_DATA = False


class Calf(ClassifierMixin, TransformerMixin, BaseEstimator):
    """Course approximation linear function"""

    def __init__(self, grid=(-1, 1), auc_tol=1e-6, order_col=False, verbose=False):
        self.grid = [grid] if isinstance(grid, int) else grid
        self.auc_tol = auc_tol
        self.order_col = order_col
        self.verbose = verbose

    def _validate_input(self, X, reset=False):
        if HAS_VALIDATE_DATA:
            return validate_data(self, X=X, accept_sparse=["csr", "csc", "coo"], reset=reset)
        return self._validate_data(X, accept_sparse=["csr", "csc", "coo"], reset=reset)

    def fit(self, X, y):
        if y is None:
            raise ValueError('requires y to be passed, but the target y is None')

        # Fix 1: Handle unknown object dtypes cleanly
        y_type = type_of_target(y)
        if y_type == 'unknown':
            raise ValueError("Unknown label type: target y must be binary.")
        if y_type != 'binary':
            raise ValueError(f"Only binary classification is supported. The type of the target is {y_type}.")

        if HAS_VALIDATE_DATA:
            X, y = validate_data(self, X=X, y=y, accept_sparse=["csr", "csc", "coo"], reset=True)
        else:
            X, y = self._validate_data(X=X, y=y, accept_sparse=["csr", "csc", "coo"], reset=True)

        self.classes_ = unique_labels(y)
        self.X_ = X
        self.y_ = y

        if self.verbose:
            print(f'fitting {X.shape[1]} features.')

        start = time.time()

        if issparse(X):
            self.auc_, self.weights_, self.feature_index_ = fit_hv_sparse(
                X, y, grid=self.grid, auc_tol=self.auc_tol,
                order_col=self.order_col, verbose=self.verbose
            )
        else:
            self.auc_, self.weights_, self.feature_index_ = fit_hv(
                X, y, grid=self.grid, verbose=self.verbose
            )

        self.fit_time_ = time.time() - start

        self.coef_ = [0] * X.shape[1]
        for i, w in zip(self.feature_index_, self.weights_):
            self.coef_[i] = w

        return self

    def decision_function(self, X):
        check_is_fitted(self)
        X = self._validate_input(X, reset=False)

        # Fix 2: Ensure the matrix is sliceable
        if issparse(X):
            X = X.tocsr()

        scores = np.array(
            minmax_scale(
                predict(X[:, self.feature_index_], self.weights_),
                feature_range=(-1, 1)
            )
        )
        return scores

    def predict(self, X):
        check_is_fitted(self)
        X = self._validate_input(X, reset=False)

        if len(self.classes_) < 2:
            y_class = self.y_
        else:
            y_class = np.heaviside(self.decision_function(X), 0).astype(int)
            y_class = [self.classes_[x] for x in y_class]
        return np.array(y_class)

    def predict_proba(self, X):
        check_is_fitted(self)
        X = self._validate_input(X, reset=False)
        y_proba = expit(self.decision_function(X))
        class_prob = np.column_stack((1 - y_proba, y_proba))
        return class_prob

    def transform(self, X):
        check_is_fitted(self)
        X = self._validate_input(X, reset=False)

        # Fix 2: Ensure the matrix is sliceable
        if issparse(X):
            X = X.tocsr()

        return X[:, self.feature_index_]

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)

    def _more_tags(self):
        return {'poor_score': True, 'non_deterministic': True, 'binary_only': True}

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.classifier_tags.poor_score = True
        tags.classifier_tags.multi_class = False
        tags.input_tags.sparse = True
        tags.non_deterministic = True
        tags.estimator_type = "classifier"
        return tags