import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from feature_engine.encoding import StringSimilarityEncoder


def test_encode_top_categories():

    df = pd.DataFrame(
        {
            "var_A": ["A"] * 5
            + ["B"] * 11
            + ["C"] * 4
            + ["D"] * 9
            + ["E"] * 2
            + ["F"] * 2
            + ["G"] * 7,
            "var_B": ["A"] * 11
            + ["B"] * 7
            + ["C"] * 4
            + ["D"] * 9
            + ["E"] * 2
            + ["F"] * 2
            + ["G"] * 5,
            "var_C": ["A"] * 4
            + ["B"] * 5
            + ["C"] * 11
            + ["D"] * 9
            + ["E"] * 2
            + ["F"] * 2
            + ["G"] * 7,
        }
    )

    encoder = StringSimilarityEncoder(top_categories=4)
    X = encoder.fit_transform(df)

    # test init params
    assert encoder.top_categories == 4
    # test fit attr
    transf = {
        "var_A_D": 9,
        "var_A_B": 11,
        "var_A_A": 5,
        "var_A_G": 7,
        "var_B_A": 11,
        "var_B_D": 9,
        "var_B_G": 5,
        "var_B_B": 7,
        "var_C_D": 9,
        "var_C_C": 11,
        "var_C_G": 7,
        "var_C_B": 5,
    }

    # test fit attr
    assert encoder.variables_ == ["var_A", "var_B", "var_C"]
    assert encoder.n_features_in_ == 3
    assert encoder.encoder_dict_ == {
        "var_A": ["B", "D", "G", "A"],
        "var_B": ["A", "D", "B", "G"],
        "var_C": ["C", "D", "G", "B"],
    }
    # test transform output
    for col in transf.keys():
        assert X[col].sum() == transf[col]
    assert "var_B" not in X.columns
    assert "var_B_F" not in X.columns


def test_error_if_top_categories_not_integer():
    with pytest.raises(ValueError):
        StringSimilarityEncoder(top_categories=0.5)


def test_error_if_handle_missing_invalid():
    with pytest.raises(ValueError):
        StringSimilarityEncoder(handle_missing='propagate')


def test_nan_behaviour(df_enc_big, df_enc_big_na):
    with pytest.raises(ValueError):
        encoder = StringSimilarityEncoder(handle_missing='error')
        encoder.fit(df_enc_big_na)

    with pytest.raises(ValueError):
        encoder = StringSimilarityEncoder(handle_missing='error')
        encoder.fit(df_enc_big)
        encoder.transform(df_enc_big_na)

    encoder = StringSimilarityEncoder(handle_missing='impute')
    X = encoder.fit_transform(df_enc_big_na)
    assert X.isna().sum() == 0

    encoder = StringSimilarityEncoder(handle_missing='ignore')
    X = encoder.fit_transform(df_enc_big_na)
    assert X.isna() == df_enc_big_na.isna()


def test_get_feature_names_out(df_enc_binary):
    original_features = ["var_num"]
    input_features = ["var_A", "var_B", "var_C", "var_D"]

    tr = StringSimilarityEncoder()
    tr.fit(df_enc_binary)

    out = [
        "var_A_A",
        "var_A_B",
        "var_A_C",
        "var_B_A",
        "var_B_B",
        "var_B_C",
        "var_C_AHA",
        "var_C_UHU",
        "var_D_OHO",
        "var_D_EHE",
    ]

    assert tr.get_feature_names_out(input_features=None) == original_features + out
    assert tr.get_feature_names_out(input_features=input_features) == out
    assert tr.get_feature_names_out(input_features=input_features[0:2]) == out[0:6]
    assert tr.get_feature_names_out(input_features=[input_features[0]]) == out[0:3]

    tr = StringSimilarityEncoder(top_categories=1)
    tr.fit(df_enc_binary)

    out = ["var_A_B", "var_B_A", "var_C_AHA", "var_D_EHE"]

    assert tr.get_feature_names_out(input_features=None) == original_features + out
    assert tr.get_feature_names_out(input_features=input_features) == out
    assert tr.get_feature_names_out(input_features=input_features[0:2]) == out[0:2]
    assert tr.get_feature_names_out(input_features=[input_features[3]]) == [out[3]]

    with pytest.raises(ValueError):
        tr.get_feature_names_out("var_A")

    with pytest.raises(ValueError):
        tr.get_feature_names_out(["var_A", "hola"])


def test_get_feature_names_out_from_pipeline(df_enc_binary):
    original_features = ["var_num"]
    input_features = ["var_A", "var_B", "var_C", "var_D"]

    tr = Pipeline([("transformer", StringSimilarityEncoder())])
    tr.fit(df_enc_binary)

    out = [
        "var_A_A",
        "var_A_B",
        "var_A_C",
        "var_B_A",
        "var_B_B",
        "var_B_C",
        "var_C_AHA",
        "var_C_UHU",
        "var_D_OHO",
        "var_D_EHE",
    ]

    assert tr.get_feature_names_out(input_features=None) == original_features + out
    assert tr.get_feature_names_out(input_features=input_features) == out
    assert tr.get_feature_names_out(input_features=input_features[0:2]) == out[0:6]
    assert tr.get_feature_names_out(input_features=[input_features[0]]) == out[0:3]