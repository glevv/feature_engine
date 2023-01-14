import numpy as np
import pytest
from sklearn.exceptions import NotFittedError

from feature_engine.discretisation import IncreasingWidthDiscretiser


def test_automatically_find_variables_and_return_as_numeric(df_normal_dist):
    # test case 1: automatically select variables, return_object=False
    transformer = IncreasingWidthDiscretiser(
        bins=10, variables=None, return_object=False
    )
    X = transformer.fit_transform(df_normal_dist*10)  # for numerical stability

    # fit parameters
    min_, max_ = df_normal_dist["var"].min()*10, df_normal_dist["var"].max()*10
    increment = np.power(max_ - min_, 1.0 / 10)
    bins = np.r_[min_, min_ + np.power(increment, np.arange(1, 10 + 1))]
    bins = np.sort(bins)
    bins = list(bins)
    bins[0] = float("-inf")
    bins[len(bins) - 1] = float("inf")

    # transform output
    X_t = [x for x in range(0, 10)]
    val_counts = [9, 2, 5, 8, 11, 11, 24, 10, 13, 7]

    # init params
    assert transformer.bins == 10
    assert transformer.variables is None
    assert transformer.return_object is False
    # fit params
    assert transformer.variables_ == ["var"]
    assert transformer.n_features_in_ == 1
    # transform params
    assert (transformer.binner_dict_["var"] == bins).all()
    assert all(x for x in X["var"].unique() if x not in X_t)
    # in equal width discretisation, intervals get different number of values
    assert all(x for x in X["var"].value_counts() if x not in val_counts)


def test_automatically_find_variables_and_return_as_object(df_normal_dist):
    transformer = IncreasingWidthDiscretiser(
        bins=10, variables=None, return_object=True
    )
    X = transformer.fit_transform(df_normal_dist)
    assert X["var"].dtypes == "O"


def test_error_when_bins_not_number():
    with pytest.raises(ValueError):
        IncreasingWidthDiscretiser(bins="other")


def test_error_if_return_object_not_bool():
    with pytest.raises(ValueError):
        IncreasingWidthDiscretiser(return_object="other")


def test_error_if_input_df_contains_na_in_fit(df_na):
    # test case 3: when dataset contains na, fit method
    with pytest.raises(ValueError):
        transformer = IncreasingWidthDiscretiser()
        transformer.fit(df_na)


def test_error_if_input_df_contains_na_in_transform(df_vartypes, df_na):
    # test case 4: when dataset contains na, transform method
    with pytest.raises(ValueError):
        transformer = IncreasingWidthDiscretiser()
        transformer.fit(df_vartypes)
        transformer.transform(df_na[["Name", "City", "Age", "Marks", "dob"]])


def test_non_fitted_error(df_vartypes):
    with pytest.raises(NotFittedError):
        transformer = IncreasingWidthDiscretiser()
        transformer.transform(df_vartypes)
