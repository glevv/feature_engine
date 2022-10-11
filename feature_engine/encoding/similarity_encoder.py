from difflib import SequenceMatcher
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.utils.validation import check_is_fitted

from feature_engine._docstrings.fit_attributes import (
    _feature_names_in_docstring,
    _n_features_in_docstring,
    _variables_attribute_docstring,
)
from feature_engine._docstrings.init_parameters import (
    _ignore_format_docstring,
    _variables_categorical_docstring,
)
from feature_engine._docstrings.methods import _fit_transform_docstring
from feature_engine._docstrings.substitute import Substitution
from feature_engine.dataframe_checks import _check_contains_na, check_X
from feature_engine.encoding.base_encoder import (
    CategoricalInitMixin,
    CategoricalMethodsMixin,
)


def _gpm_fast(x1: str, x2: str) -> float:
    return SequenceMatcher(None, str(x1), str(x2)).quick_ratio()


_gpm_fast_vec = np.vectorize(_gpm_fast)


@Substitution(
    ignore_format=_ignore_format_docstring,
    variables=_variables_categorical_docstring,
    variables_=_variables_attribute_docstring,
    feature_names_in_=_feature_names_in_docstring,
    n_features_in_=_n_features_in_docstring,
    fit_transform=_fit_transform_docstring,
)
class StringSimilarityEncoder(CategoricalInitMixin, CategoricalMethodsMixin):
    """
    The StringSimilarityEncoder() replaces categorical variables by a set of
    float variables representing similarity between unique categories in the variable.
    This new variables will have values in range between 0 and 1, where 0 is the least
    similar and 1 is the exact match.
    The similarity measure is gestalt pattern matching.
    This encoding is an alternative to OneHotEncoder in the case of poorly
    defined categorical variables.

    The encoder will create k variables, where k is the number of unique categories.

    The encoder has the additional option to generate similarity variables only for the
    most popular categories, that is, the categories that are shared by the
    majority of the observations in the dataset. This behaviour can be specified with
    the parameter `top_categories`.

    The encoder has the option to specify the behaviour when NaN is present in the
    variable, see parameter `handle_missing`.

    The encoder will encode only categorical variables by default (type 'object' or
    'categorical'). You can pass a list of variables to encode. Alternatively, the
    encoder will find and encode all categorical variables (type 'object' or
    'categorical').

    With `ignore_format=True` you have the option to encode numerical variables as well.
    The procedure is identical, you can either enter the list of variables to encode, or
    the transformer will automatically select all variables.

    The encoder first finds the categories to be encoded for each variable (fit). The
    encoder then creates one dummy variable per category for each variable
    (transform).

    Parameters
    ----------
    top_categories: int, default=None
        If None, dummy variables will be created for each unique category of the
        variable. Alternatively, we can indicate in the number of most frequent
        categories to encode. In this case, similarity variables will be created
        only for those popular categories and the rest will be ignored.

    handle_missing : str, default='impute'
        Action to perform when NaN is seen.
            'error' - raise an error;
            'impute' - impute NaN with an empty string;
            'ignore' - ignore NaN and leave them in resulting columns.

    {variables}

    {ignore_format}

    Attributes
    ----------
    encoder_dict_:
        Dictionary with the categories for which dummy variables will be created.

    {variables_}

    {feature_names_in_}

    {n_features_in_}

    Methods
    -------
    fit:
        Learn the unique categories per variable

    {fit_transform}

    transform:
        Replace the categorical variables by the binary variables.

    Notes
    -----
    This encoder will encode new categories by measuring string similarity between
    seen and unseen categories.

    No preprocessing is applied, so it's on user to prepare string categorical
    variables for this transformer.

    This encoder has option to ignore format of the column. This allow user to encode
    'numerical' categories that are more useful to count as strings, than numbers.

    The original categorical variables are removed from the returned dataset when we
    apply the transform() method. In their place, the binary variables are returned.

    See Also
    --------
    feature_engine.encoding.OneHotEncoder
    dirty_cat.SimilarityEncoder

    References
    ----------
    .. [1] Cerda P, Varoquaux G, Kégl B. "Similarity encoding for learning with dirty
       categorical variables". Machine Learning, Springer Verlag, 2018.
    .. [2] Cerda P, Varoquaux G. "Encoding high-cardinality string categorical
       variables". IEEE Transactions on Knowledge & Data Engineering, 2020.
    """

    def __init__(
        self,
        top_categories: Union[None, int] = None,
        handle_missing: str = "impute",
        variables: Union[None, int, str, List[Union[str, int]]] = None,
        ignore_format: bool = False,
    ):
        if top_categories and not isinstance(top_categories, int):
            raise ValueError(
                f"top_categories takes only integers. Got {top_categories!r} instead."
            )
        if handle_missing not in ("error", "impute", "ignore"):
            raise ValueError(
                "handle_missing should be one of 'error', 'impute' or 'ignore'."
                f" Got {handle_missing!r} instead."
            )
        super().__init__(variables, ignore_format)
        self.top_categories = top_categories
        self.handle_missing = handle_missing

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Learns the unique categories per variable. If top_categories is indicated,
        it will learn the most popular categories. Alternatively, it learns all
        unique categories per variable.

        Parameters
        ----------

        X: pandas dataframe of shape = [n_samples, n_features]
            The training input samples.
            Can be the entire dataframe, not just the variables to encode.

        y: pandas series, default=None
            Target. It is not needed in this encoded. You can pass y or None.
        """

        X = check_X(X)
        self._check_or_select_variables(X)
        self._get_feature_names_in(X)
        self.encoder_dict_ = {}

        if self.handle_missing == "error":
            _check_contains_na(X, self.variables_)
            for var in self.variables_:
                self.encoder_dict_[var] = (
                    X[var].value_counts().head(self.top_categories).index.tolist()
                )
        elif self.handle_missing == "impute":
            for var in self.variables_:
                self.encoder_dict_[var] = (
                    X[var]
                    .fillna("")
                    .value_counts()
                    .head(self.top_categories)
                    .index.tolist()
                )
        elif self.handle_missing == "ignore":
            for var in self.variables_:
                self.encoder_dict_[var] = (
                    X[var]
                    .value_counts(dropna=True)
                    .head(self.top_categories)
                    .index.tolist()
                )

        self._check_encoding_dictionary()

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Replaces the categorical variables with the similarity variables.

        Parameters
        ----------
        X: pandas dataframe of shape = [n_samples, n_features]
            The data to transform.

        Returns
        -------
        X_new: pandas dataframe.
            The transformed dataframe. The shape of the dataframe will be different from
            the original as it includes the similarity variables in place of the of the
            original categorical ones.
        """

        check_is_fitted(self)
        X = self._check_transform_input_and_state(X)
        if self.handle_missing == "error":
            _check_contains_na(X, self.variables_)

        new_values = []
        for var in self.variables_:
            if self.handle_missing == "impute":
                X[var] = X[var].fillna("")
            new_categories = X[var].dropna().unique()
            column_encoder_dict = {
                x: _gpm_fast_vec(x, self.encoder_dict_[var]) for x in new_categories
            }
            column_encoder_dict[np.nan] = [np.nan] * len(self.encoder_dict_[var])
            encoded = np.vstack(X[var].map(column_encoder_dict).values)
            if self.handle_missing == "ignore":
                encoded[X[var].isna(), :] = np.nan
            new_values.append(encoded)

        new_features = self._get_new_features_name()
        X.loc[:, new_features] = np.hstack(new_values)

        return X.drop(self.variables_, axis=1)

    def _get_new_features_name(self) -> List:
        """Return names of the created features."""
        feature_names = []
        for feature in self.variables_:
            for category in self.encoder_dict_[feature]:
                if category == "":
                    feature_names.append(f"{feature}_nan")
                else:
                    feature_names.append(f"{feature}_{category}")

        return feature_names

    def _add_new_feature_names(self, feature_names) -> List:
        """Adds new features to df columns, and removes categoricals."""
        feature_names = feature_names + self._get_new_features_name()
        feature_names = [f for f in feature_names if f not in self.variables_]

        return feature_names

    def inverse_transform(self, X: pd.DataFrame):
        """inverse_transform is not implemented for this transformer."""
        raise NotImplementedError(
            "inverse_transform is not implemented for this transformer."
        )
