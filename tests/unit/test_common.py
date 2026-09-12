from sklearn.utils.estimator_checks import parametrize_with_checks
from calfcv import Calf, CalfCV

@parametrize_with_checks([Calf(), CalfCV()])
def test_all_estimators(estimator, check):
    """
    Validates that Calf and CalfCV adhere strictly to the scikit-learn
    BaseEstimator and ClassifierMixin API conventions.
    """
    check(estimator)