import numpy as np
from scipy.sparse import issparse
from sklearn.metrics import roc_auc_score
from joblib import Parallel, delayed


def predict(X, w):
    """Predict the classes from the weights and features.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input features and samples.
    w : array-like of shape (n_features,)
        The weights applied to the features.

    Returns
    -------
    y_pred : ndarray of shape (n_samples,)
        The prediction of the ground truth.
    """
    if issparse(X):
        Z = X.multiply(w)
        y_pred = np.asarray(Z.sum(axis=1)).ravel()
    else:
        y_pred = np.sum(X * w, axis=1)
    return y_pred


def _column_task(i, V, y, grid):
    """Evaluate AUC for predicting a single column.

    Parameters
    ----------
    i : int
        The column index to evaluate.
    V : ndarray of shape (n_samples,)
        A single 1D array column of the training input features.
    y : array-like of shape (n_samples,)
        The target vector.
    grid : array-like
        A list or array of candidate weights.

    Returns
    -------
    auc : float
        The maximum prediction AUC for column i.
    w : float
        The weight that yields the highest AUC.
    i : int
        The column index.
    """
    best_auc = -1.0
    best_w = None
    classes = np.unique(y)

    for w in grid:
        y_score = np.nan_to_num(V * w, copy=False)

        # 1. Binary target: standard single ROC-AUC calculation
        if len(classes) == 2:
            auc = roc_auc_score(y_true=(y == classes[1]), y_score=y_score)

        # 2. Multiclass target (e.g., Iris during sklearn estimator checks): OvR average
        else:
            auc = np.mean(
                [roc_auc_score(y_true=(y == c), y_score=y_score) for c in classes]
            )

        if auc >= best_auc:
            best_auc = auc
            best_w = w

    return best_auc, best_w, i


def fit_columns(X, y, grid, n_jobs=-1):
    """Fit columns in parallel to find individual column AUCs.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input features and samples.
    y : array-like of shape (n_samples,)
        The target vector.
    grid : array-like
        A list or array of candidate weights.
    n_jobs : int, default=-1
        The number of jobs to run in parallel. -1 means using all processors.

    Returns
    -------
    candidates : list of tuples
        A sorted list of tuples in descending order of AUC.
        Each tuple contains (auc, weight, column_index).
    """
    is_sp = issparse(X)
    if is_sp:
        X = X.tocsc()

    def get_col(j):
        return X[:, j].toarray().ravel() if is_sp else X[:, j]

    candidates = Parallel(n_jobs=n_jobs)(
        delayed(_column_task)(i, get_col(i), y, grid) for i in range(X.shape[1])
    )
    return sorted(candidates, reverse=True)


def _fit_forward_selection(X, y, grid, auc_tol=1e-6, order_col=False, verbose=False):
    """Unified forward selection engine for dense and sparse matrices.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input features and samples.
    y : array-like of shape (n_samples,)
        The ground truth vector.
    grid : array-like
        A list or array of candidate weights.
    auc_tol : float, default=1e-6
        Tolerance above max AUC for inclusion of a feature index.
    order_col : bool, default=False
        Whether to order the columns by individual AUC prior to fitting.
    verbose : bool, default=False
        If True, print status messages.

    Returns
    -------
    auc : list of float
        The list of cumulative maximum AUCs at each step.
    weights : list of float
        The list of optimal weights corresponding to the selected features.
    index : list of int
        The list of feature indices selected.
    """
    n_samples, n_features = X.shape
    is_sp = issparse(X)
    if is_sp:
        X = X.tocsc()

    if order_col:
        tups = fit_columns(X, y, grid)
        col_order = [i for _, _, i in tups]
    else:
        col_order = range(n_features)

    count = 0
    weights = []
    auc = []
    index = []

    # Safely initialize cumulative scores to exact zeros
    U = np.zeros(n_samples)

    for i in col_order:
        V = X[:, i].toarray().ravel() if is_sp else X[:, i]

        candidates = []
        for w_idx, w in enumerate(grid):
            Z = U + V * w
            y_score = np.nan_to_num(Z, copy=False)
            # Store w_idx as the explicit, deterministic tie-breaker
            candidates.append((roc_auc_score(y_true=y, y_score=y_score), w_idx, Z, w))

        # Max prioritizes highest AUC [0], then highest w_idx [1] if AUCs tie
        best_candidate = max(candidates, key=lambda item: (item[0], item[1]))
        max_auc, _, next_U, w_c = best_candidate

        if not auc or max_auc > max(auc) + auc_tol:
            weights.append(w_c)
            index.append(i)
            U = next_U

            if auc and verbose:
                print(
                    f"Count {count} of {n_features} fit feature {i} "
                    f"feature auc: {round(max_auc, 4)} > max auc: {round(max(auc), 4)} "
                    f"weight: {w_c} selected features: {len(index)} auc tol: {auc_tol}"
                )
        else:
            if count % 100 == 0 and verbose:
                print(
                    f"Count {count} of {n_features} max auc: {round(max(auc), 4)} "
                    f"number of contributing features {len(index)}"
                )

        count += 1
        auc.append(max_auc)

        if max(auc) >= 0.999:
            if verbose:
                print(
                    f"found {len(index)} features that contribute positive auc.\n"
                    "auc threshold reached, breaking ..."
                )
            break

    return auc, weights, index


def fit_hv_sparse(X, y, grid, auc_tol=1e-6, order_col=False, verbose=False):
    """Find the weights that best fit sparse X using points from the grid.

    Parameters
    ----------
    X : sparse matrix of shape (n_samples, n_features)
        The training input features and samples.
    y : array-like of shape (n_samples,)
        The ground truth vector.
    grid : array-like
        A list or array of candidate weights.
    auc_tol : float, default=1e-6
        Tolerance above max AUC for inclusion of a feature index.
    order_col : bool, default=False
        Whether to order the columns by individual AUC prior to fitting.
    verbose : bool, default=False
        If True, print status messages.

    Returns
    -------
    auc : list of float
        The list of cumulative maximum AUCs at each step.
    weights : list of float
        The list of optimal weights corresponding to the selected features.
    index : list of int
        The list of feature indices selected.
    """
    return _fit_forward_selection(
        X, y, grid, auc_tol=auc_tol, order_col=order_col, verbose=verbose
    )


def fit_hv(X, y, grid, auc_tol=1e-6, order_col=False, verbose=False):
    """Find the weights that best fit dense X using points from the grid.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        The training input features and samples.
    y : array-like of shape (n_samples,)
        The ground truth vector.
    grid : array-like
        A list or array of candidate weights.
    auc_tol : float, default=1e-6
        Tolerance above max AUC for inclusion of a feature index.
    order_col : bool, default=False
        Whether to order the columns by individual AUC prior to fitting.
    verbose : bool, default=False
        If True, print status messages.

    Returns
    -------
    auc : list of float
        The list of cumulative maximum AUCs at each step.
    weights : list of float
        The list of optimal weights corresponding to the selected features.
    index : list of int
        The list of feature indices selected.
    """
    return _fit_forward_selection(
        X, y, grid, auc_tol=auc_tol, order_col=order_col, verbose=verbose
    )
