import time
import numpy as np
from scipy.sparse import issparse
from sklearn.metrics import roc_auc_score
from joblib import Parallel, delayed


def predict(X, w):
    """Predict the classes from the weights and features."""
    if issparse(X):
        Z = X.multiply(w)
        y_pred = np.asarray(Z.sum(axis=1)).ravel()
    else:
        y_pred = np.sum(X * w, axis=1)
    return y_pred


def _column_task(i, X_col, y, grid):
    """Evaluate auc for predicting a single column."""
    result = []
    for w in grid:
        Z = X_col * w
        y_score = np.nan_to_num(Z.toarray(), copy=False).ravel()
        result.append(
            (
                roc_auc_score(y_true=y, y_score=y_score),
                time.time(),
                w
            )
        )
    auc, _, w = max(result)
    return auc, w, i


def fit_columns(X, y, grid, n_jobs=-1):
    """Fit using joblib parallelization."""
    X_csc = X.tocsc()
    candidates = Parallel(n_jobs=n_jobs)(
        delayed(_column_task)(i, X_csc[:, i], y, grid) for i in range(X.shape[1])
    )
    return sorted(candidates, reverse=True)


def fit_hv_sparse(X, y, grid, auc_tol=1e-6, order_col=False, verbose=False):
    """Find the weights that best fit sparse X using points from grid."""
    X_csc = X.tocsc()
    if order_col:
        tups = fit_columns(X_csc, y, grid)
        col_order = [i for _, _, i in tups]
    else:
        col_order = range(X.shape[1])

    count = 0
    weights = []
    auc = []
    index = []
    U = X_csc[:, 0] * 0

    for i in col_order:
        V = X_csc[:, i]
        candidates = []
        for w in grid:
            Z = U + V * w
            y_score = np.nan_to_num(Z.toarray().ravel())
            candidates.append(
                (
                    roc_auc_score(y_true=y, y_score=y_score),
                    time.time(),
                    Z,
                    w
                )
            )
        max_auc, _, U, w_c = max(candidates)

        if not auc or max_auc > max(auc) + auc_tol:
            weights.append(w_c)
            index.append(i)

            if auc and verbose:
                print(f'Count {count} of {X.shape[1]} fit feature {i} '
                      f'feature auc: {round(max_auc, 4)} > max auc: {round(max(auc), 4)} '
                      f'weight: {w_c} selected features: {len(index)} auc tol: {auc_tol}')
        else:
            if count % 100 == 0 and verbose:
                print(f'Count {count} of {X.shape[1]} max auc: {round(max(auc), 4)} '
                      f'number of contributing features {len(index)}')

        count += 1
        auc.append(max_auc)

        if max(auc) >= 0.999:
            if verbose:
                print(f'found {len(index)} features that contribute positive auc.\n'
                      'auc threshold reached, breaking ...')
            break

    return auc, weights, index


def fit_hv(X, y, grid, verbose=False):
    """Find the weights that best fit dense X using points from grid."""
    weights = []
    auc = []
    index = []
    U = np.empty((X.shape[0]))

    for i in range(X.shape[1]):
        V = X[:, i]
        candidates = []
        for w in grid:
            y_score = np.nan_to_num(U + V * w)
            candidates.append(
                (
                    roc_auc_score(y_true=y, y_score=y_score),
                    time.time(),
                    y_score,
                    w
                )
            )
        max_auc, _, U, w_c = sorted(candidates, reverse=True)[0]

        if not auc or max_auc > max(auc):
            weights.append(w_c)
            index.append(i)

        auc.append(max_auc)

        if verbose:
            if max_auc > max(auc):
                print(f'fit feature {i} of {X.shape[1]} feature auc: {round(max_auc, 4)} '
                      f'> max auc: {round(max(auc), 4)} weight: {w_c} '
                      f'number of contributing features {len(index)}')
            else:
                print(f'fit feature {i} of {X.shape[1]} feature auc: {round(max_auc, 4)} '
                      f'<= max auc: {round(max(auc), 4)} weight: 0 '
                      f'number of contributing features {len(index)}')

        if max(auc) >= 0.999:
            if verbose:
                print(f'found {len(index)} features that contribute positive auc.\n'
                      'auc threshold reached, breaking ...')
            break

    return auc, weights, index