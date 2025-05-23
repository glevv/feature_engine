"""
This file is only intended to help understand check_estimator tests on Feature-engine
transformers. It is not run as part of the battery of acceptance tests. Works up to
sklearn < 1.6.
"""

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.utils.estimator_checks import parametrize_with_checks

from feature_engine.creation import (
    CyclicalFeatures,
    DecisionTreeFeatures,
    MathFeatures,
    RelativeFeatures,
)
from feature_engine.encoding import (
    CountFrequencyEncoder,
    DecisionTreeEncoder,
    MeanEncoder,
    OneHotEncoder,
    OrdinalEncoder,
    RareLabelEncoder,
    StringSimilarityEncoder,
    WoEEncoder,
)
from feature_engine.imputation import (
    AddMissingIndicator,
    ArbitraryNumberImputer,
    CategoricalImputer,
    DropMissingData,
    EndTailImputer,
    MeanMedianImputer,
    RandomSampleImputer,
)
from feature_engine.outliers import ArbitraryOutlierCapper, OutlierTrimmer, Winsorizer
from feature_engine.selection import (
    MRMR,
    DropConstantFeatures,
    DropCorrelatedFeatures,
    DropDuplicateFeatures,
    DropFeatures,
    DropHighPSIFeatures,
    ProbeFeatureSelection,
    RecursiveFeatureAddition,
    RecursiveFeatureElimination,
    SelectByInformationValue,
    SelectByShuffling,
    SelectBySingleFeaturePerformance,
    SelectByTargetMeanPerformance,
    SmartCorrelatedSelection,
)
from feature_engine.timeseries.forecasting import (
    ExpandingWindowFeatures,
    LagFeatures,
    WindowFeatures,
)
from feature_engine.transformation import (
    ArcsinTransformer,
    BoxCoxTransformer,
    LogTransformer,
    PowerTransformer,
    ReciprocalTransformer,
    YeoJohnsonTransformer,
)
from feature_engine.wrappers import SklearnTransformerWrapper


# creation
@parametrize_with_checks(
    [
        DecisionTreeFeatures(regression=False),
        CyclicalFeatures(),
        MathFeatures(variables=["x0", "x1"], func="mean", missing_values="ignore"),
        RelativeFeatures(
            variables=["x0", "x1"],
            reference=["x0"],
            func=["add"],
            missing_values="ignore",
        ),
    ]
)
def test_sklearn_compatible_creator(estimator, check):
    check(estimator)


# imputation
@parametrize_with_checks(
    [
        MeanMedianImputer(),
        ArbitraryNumberImputer(),
        CategoricalImputer(fill_value=0, ignore_format=True),
        EndTailImputer(),
        AddMissingIndicator(),
        RandomSampleImputer(),
        DropMissingData(),
    ]
)
def test_sklearn_compatible_imputer(estimator, check):
    check(estimator)


# encoding
@parametrize_with_checks(
    [
        CountFrequencyEncoder(ignore_format=True),
        DecisionTreeEncoder(regression=False, ignore_format=True),
        MeanEncoder(ignore_format=True),
        OneHotEncoder(ignore_format=True),
        OrdinalEncoder(ignore_format=True),
        RareLabelEncoder(
            tol=0.00000000001,
            n_categories=100000000000,
            replace_with=10,
            ignore_format=True,
        ),
        WoEEncoder(ignore_format=True),
        StringSimilarityEncoder(ignore_format=True),
    ]
)
def test_sklearn_compatible_encoder(estimator, check):
    check(estimator)


# outliers
@parametrize_with_checks(
    [
        ArbitraryOutlierCapper(max_capping_dict={"x0": 10}),
        OutlierTrimmer(),
        Winsorizer(),
    ]
)
def test_sklearn_compatible_outliers(estimator, check):
    check(estimator)


# transformers
@parametrize_with_checks(
    [
        ArcsinTransformer(),
        BoxCoxTransformer(),
        LogTransformer(),
        PowerTransformer(),
        ReciprocalTransformer(),
        YeoJohnsonTransformer(),
    ]
)
def test_sklearn_compatible_transformer(estimator, check):
    check(estimator)


# selectors
@parametrize_with_checks(
    [
        DropFeatures(features_to_drop=["x0"]),
        DropConstantFeatures(missing_values="ignore"),
        DropDuplicateFeatures(),
        DropCorrelatedFeatures(),
        SmartCorrelatedSelection(),
        DropHighPSIFeatures(bins=5),
        SelectByShuffling(
            LogisticRegression(max_iter=2, random_state=1), scoring="accuracy"
        ),
        SelectBySingleFeaturePerformance(
            LogisticRegression(max_iter=2, random_state=1), scoring="accuracy"
        ),
        RecursiveFeatureAddition(
            LogisticRegression(max_iter=2, random_state=1), scoring="accuracy"
        ),
        RecursiveFeatureElimination(
            LogisticRegression(max_iter=2, random_state=1),
            scoring="accuracy",
            threshold=-100,
        ),
        SelectByTargetMeanPerformance(scoring="roc_auc", bins=3, regression=False),
        SelectByInformationValue(),
        MRMR(),
        ProbeFeatureSelection(estimator=LogisticRegression()),
    ]
)
def test_sklearn_compatible_selectors(estimator, check):
    check(estimator)


# wrappers
@parametrize_with_checks([SklearnTransformerWrapper(SimpleImputer())])
def test_sklearn_compatible_wrapper(estimator, check):
    check(estimator)


# test_forecasting
@parametrize_with_checks(
    [
        LagFeatures(missing_values="ignore"),
        WindowFeatures(missing_values="ignore"),
        ExpandingWindowFeatures(missing_values="ignore"),
    ]
)
def test_sklearn_compatible_forecasters(estimator, check):
    check(estimator)
