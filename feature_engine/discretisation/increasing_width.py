from typing import List, Optional, Union

import pandas as pd
import numpy as np

from feature_engine._docstrings.fit_attributes import (
    _feature_names_in_docstring,
    _n_features_in_docstring,
    _variables_attribute_docstring,
)
from feature_engine._docstrings.init_parameters import _variables_numerical_docstring
from feature_engine._docstrings.methods import _fit_transform_docstring
from feature_engine._docstrings.substitute import Substitution
from feature_engine._variable_handling.init_parameter_checks import (
    _check_init_parameter_variables,
)
from feature_engine.discretisation.base_discretiser import BaseDiscretiser


@Substitution(
    return_object=BaseDiscretiser._return_object_docstring,
    return_boundaries=BaseDiscretiser._return_boundaries_docstring,
    binner_dict_=BaseDiscretiser._binner_dict_docstring,
    fit=BaseDiscretiser._fit_docstring,
    transform=BaseDiscretiser._transform_docstring,
    variables=_variables_numerical_docstring,
    variables_=_variables_attribute_docstring,
    feature_names_in_=_feature_names_in_docstring,
    n_features_in_=_n_features_in_docstring,
    fit_transform=_fit_transform_docstring,
)
class IncreasingWidthDiscretiser(BaseDiscretiser):
    """
    The IncreasingWidthDiscretiser() divides continuous numerical variables into
    intervals of increasing width with equal increments. Note that the
    proportion of observations per interval may vary.

    The size of the interval will follow geometric progression.

    The IncreasingWidthDiscretiser() works only with numerical variables.
    A list of variables can be passed as argument. Alternatively, the discretiser
    will automatically select all numerical variables.

    The IncreasingWidthDiscretiser() first finds the boundaries for the intervals for
    each variable. Then, it transforms the variables, that is, sorts the values into
    the intervals.

    More details in the :ref:`User Guide <increasing_width_discretiser>`.

    Parameters
    ----------
    {variables}

    bins: int, default=10
        Desired number of intervals / bins.

    {return_object}

    {return_boundaries}

    Attributes
    ----------
    {binner_dict_}

    {variables_}

    {feature_names_in_}

    {n_features_in_}

    Methods
    -------
    {fit}

    {fit_transform}

    {transform}

    References
    ----------
    .. [1]  J. Reiser, "Classification Systems",
        https://www.slideshare.net/johnjreiser/classification-systems

    """

    def __init__(
        self,
        variables: Union[None, int, str, List[Union[str, int]]] = None,
        bins: int = 10,
        return_object: bool = False,
        return_boundaries: bool = False,
    ):

        if not isinstance(bins, int):
            raise ValueError(f"bins must be an integer. Got {bins} instead.")

        super().__init__(return_object, return_boundaries)

        self.bins = bins
        self.variables = _check_init_parameter_variables(variables)

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Learn the boundaries of the equal width intervals / bins for each
        variable.

        Parameters
        ----------
        X: pandas dataframe of shape = [n_samples, n_features]
            The training dataset. Can be the entire dataframe, not just the variables
            to be transformed.
        y: None
            y is not needed in this encoder. You can pass y or None.
        """

        # check input dataframe
        X = super().fit(X)

        # fit
        self.binner_dict_ = {}

        for var in self.variables_:
            min_, max_ = X[var].min(), X[var].max()
            increment = np.power(max_ - min_, 1.0 / self.bins)
            bins = np.r_[min_, min_ + np.power(increment, np.arange(1, self.bins + 1))]
            bins = np.sort(bins)

            # Prepend/Append infinities
            bins = list(bins)
            bins[0] = float("-inf")
            bins[len(bins) - 1] = float("inf")
            self.binner_dict_[var] = bins

        return self