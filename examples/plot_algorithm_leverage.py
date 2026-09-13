"""
========================================================================
CALF as a Supervised Feature Selection Preprocessor
========================================================================

This example demonstrates using :class:`Calf` as a dimensionality reduction
preprocessor inside a Scikit-Learn pipeline.

High-dimensional datasets with heavy noise often cause downstream continuous
classifiers (like Logistic Regression) to overfit. By inserting ``Calf`` as a
preliminary feature selector, non-informative features are pruned using discrete
forward selection prior to weight optimization.

We compare the cross-validated ROC-AUC and Accuracy of:
1. Baseline Logistic Regression (no feature selection, all 200 features)
2. CALF-preprocessed Logistic Regression (dynamic k selection)
3. SelectKBest (ANOVA F-test, hardcoded k=15) + Logistic Regression
4. RFE Preprocessor (L2 Logistic Regression, hardcoded k=15) + Logistic Regression
"""

# %%
# Imports and Synthetic Dataset Generation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.feature_selection import RFE, SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from calfcv import Calf

# Generate a high-dimensional dataset:
# Features 0..19: Informative signal
# Features 20..29: Redundant signal
# Features 30..199: Pure noise (170 columns)
X, y = make_classification(
    n_samples=1000,
    n_features=200,
    n_informative=20,
    n_redundant=10,
    n_classes=2,
    shuffle=False,  # Unshuffled so columns 0..29 are signal, 30..199 are noise
    random_state=11,
)

# %%
# Define Comparison Pipelines
pipelines = {
    "Baseline (No Selection)": make_pipeline(
        StandardScaler(), LogisticRegression(solver="liblinear", random_state=42)
    ),
    "CALF Preprocessor": make_pipeline(
        StandardScaler(),
        Calf(),
        LogisticRegression(solver="liblinear", random_state=42),
    ),
    "SelectKBest (ANOVA)": make_pipeline(
        StandardScaler(),
        SelectKBest(score_func=f_classif, k=15),
        LogisticRegression(solver="liblinear", random_state=42),
    ),
    "RFE Preprocessor": make_pipeline(
        StandardScaler(),
        RFE(
            estimator=LogisticRegression(solver="liblinear", random_state=42),
            n_features_to_select=15,
        ),
        LogisticRegression(solver="liblinear", random_state=42),
    ),
}

# %%
# Evaluate Pipelines via Stratified K-Fold CV
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
scoring = ["roc_auc", "accuracy"]

results = {
    name: cross_validate(pipe, X, y, cv=cv, scoring=scoring)
    for name, pipe in pipelines.items()
}

# %%
# Visualize Performance Comparison across CV Folds
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True)
fig.suptitle(
    "Impact of Preprocessing/Feature Selection on Downstream Logistic Regression",
    fontsize=12,
    fontweight="bold",
)

model_names = list(pipelines.keys())
auc_scores = [results[name]["test_roc_auc"] for name in model_names]
acc_scores = [results[name]["test_accuracy"] for name in model_names]

# Plot ROC-AUC
ax1.boxplot(auc_scores, tick_labels=model_names, patch_artist=True)
ax1.set_ylabel("ROC-AUC Score")
ax1.set_title("Cross-Validated ROC-AUC")
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.set_ylim(0.75, 1.05)

for i, scores in enumerate(auc_scores):
    mean_val, std_val = np.mean(scores), np.std(scores)
    max_val = np.max(scores)
    ax1.annotate(
        f"μ={mean_val:.3f}\nσ={std_val:.3f}",
        xy=(i + 1, max_val),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
        bbox=dict(
            boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="none"
        ),
    )

# Plot Accuracy
ax2.boxplot(acc_scores, tick_labels=model_names, patch_artist=True)
ax2.set_ylabel("Accuracy Score")
ax2.set_title("Cross-Validated Accuracy")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.set_ylim(0.75, 1.05)

for i, scores in enumerate(acc_scores):
    mean_val, std_val = np.mean(scores), np.std(scores)
    max_val = np.max(scores)
    ax2.annotate(
        f"μ={mean_val:.3f}\nσ={std_val:.3f}",
        xy=(i + 1, max_val),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
        bbox=dict(
            boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="none"
        ),
    )

plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# %%
# Detailed Feature Breakdown (Signal vs. Noise Analysis)
print("\n" + "=" * 60)
print("FEATURE SELECTION & SIGNAL RECOVERY ANALYSIS")
print("=" * 60)

breakdown = []

for name, pipe in pipelines.items():
    pipe.fit(X, y)

    if "calf" in pipe.named_steps:
        selected_indices = pipe.named_steps["calf"].feature_index_
    elif "selectkbest" in pipe.named_steps:
        selected_indices = np.where(pipe.named_steps["selectkbest"].get_support())[0]
    elif "rfe" in pipe.named_steps:
        selected_indices = np.where(pipe.named_steps["rfe"].support_)[0]
    else:
        selected_indices = np.arange(X.shape[1])

    # Convert to NumPy array to allow vector comparisons
    selected_indices = np.asarray(selected_indices)
    n_selected = len(selected_indices)

    # Features 0..29 are signal; 30..199 are pure noise
    signal_count = np.sum(selected_indices < 30)
    noise_count = np.sum(selected_indices >= 30)

    breakdown.append(
        {
            "Preprocessor": name,
            "Selected Features (k)": n_selected,
            "Signal Features (0..29)": f"{signal_count} / 30",
            "Noise Features (30..199)": f"{noise_count} / 170",
            "Noise Reduction": f"{((170 - noise_count) / 170) * 100:.1f}%",
            "Hyperparameter Search Needed?": (
                "No (Dynamic)"
                if "CALF" in name
                else ("Yes (Needs k)" if n_selected < 200 else "None")
            ),
        }
    )

df_breakdown = pd.DataFrame(breakdown)
print(df_breakdown.to_string(index=False))

# %%
# Key Trade-off Interpretation
# ----------------------------
# 1. Hyperparameter Search Overhead:
#    Methods like `SelectKBest` and `RFE` require the practitioner to either guess
#    the optimal `k` upfront or execute an expensive `GridSearchCV` over many candidate
#    values of `k`. CALF dynamically terminates feature selection via its internal AUC
#    plateau tolerance (`auc_tol`), removing the need for a grid search over `k`.
#
# 2. Noise Suppression:
#    By automatically filtering non-informative features without hardcoding a hyperparameter,
#    CALF suppresses pure noise features while protecting downstream models from overfitting.
