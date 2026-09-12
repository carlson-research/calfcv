from calfcv import CalfCV


def test_calfcv(data):
    X, y = data
    clf = CalfCV()
    assert clf.grid == (-1, 1)

    clf.fit(X, y)

    # Verify the scikit-learn standard trailing underscore attributes
    assert hasattr(clf, 'classes_')
    assert hasattr(clf, 'X_')
    assert hasattr(clf, 'y_')
    assert hasattr(clf, 'model_')

    y_pred = clf.predict(X)
    assert y_pred.shape == (X.shape[0],)

    # Expect 1-2 informative features to be found
    X_r = clf.transform(X)
    assert X_r.shape[1] == 3
    assert X_r.shape[0] == len(y)

    X_r = clf.fit_transform(X, y)
    assert X_r.shape[1] == 3
    assert X_r.shape[0] == len(y)