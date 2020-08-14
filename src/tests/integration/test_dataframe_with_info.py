import pytest
from sklearn.preprocessing import OneHotEncoder

from ...pd_extras.dataframe_with_info import (
    DataFrameWithInfo, FeatureOperation, _find_samples_by_type, _find_single_column_type,
    _split_columns_by_type_parallel)
from ...pd_extras.feature_enum import OperationTypeEnum
from ..dataframewithinfo_util import DataFrameMock, SeriesMock
from ..featureoperation_util import eq_featureoperation_combs


class Describe_DataFrameWithInfo:
    @pytest.mark.parametrize(
        "nan_ratio, n_columns, expected_many_nan_columns",
        [
            (0.8, 2, {"nan_0", "nan_1"}),
            (0.8, 1, {"nan_0"}),
            (0.8, 0, set()),
            (
                0.0,
                2,
                {
                    "nan_0",
                    "nan_1",
                    "not_nan_0",
                    "not_nan_1",
                    "not_nan_2",
                    "not_nan_3",
                    "not_nan_4",
                },
            ),
            (1.0, 2, {"nan_0", "nan_1"}),
        ],
    )
    def test_many_nan_columns(
        self, request, nan_ratio, n_columns, expected_many_nan_columns
    ):
        df = DataFrameMock.df_many_nans(nan_ratio, n_columns)
        df_info = DataFrameWithInfo(
            df_object=df, nan_percentage_threshold=nan_ratio - 0.01
        )

        many_nan_columns = df_info.many_nan_columns

        assert len(many_nan_columns) == len(expected_many_nan_columns)
        assert isinstance(many_nan_columns, set)
        assert many_nan_columns == expected_many_nan_columns

    @pytest.mark.parametrize(
        "n_columns, expected_same_value_columns",
        [(2, {"same_0", "same_1"}), (1, {"same_0"}), (0, set())],
    )
    def test_same_value_columns(self, request, n_columns, expected_same_value_columns):
        df = DataFrameMock.df_same_value(n_columns)
        df_info = DataFrameWithInfo(df_object=df)

        same_value_columns = df_info.same_value_cols

        assert len(same_value_columns) == len(expected_same_value_columns)
        assert isinstance(same_value_columns, set)
        assert same_value_columns == expected_same_value_columns

    @pytest.mark.parametrize(
        "n_columns, expected_trivial_columns",
        [
            (4, {"nan_0", "nan_1", "same_0", "same_1"}),
            (2, {"nan_0", "same_0"}),
            (0, set()),
        ],
    )
    def test_trivial_columns(self, request, n_columns, expected_trivial_columns):
        df = DataFrameMock.df_trivial(n_columns)
        df_info = DataFrameWithInfo(df_object=df)

        trivial_columns = df_info.trivial_columns

        assert len(trivial_columns) == len(expected_trivial_columns)
        assert isinstance(trivial_columns, set)
        assert trivial_columns == expected_trivial_columns

    @pytest.mark.parametrize(
        "feat_op_1_dict, feat_op_2_dict, is_equal_label", eq_featureoperation_combs()
    )
    def test_featureoperation_equals(
        self, request, feat_op_1_dict, feat_op_2_dict, is_equal_label
    ):
        feat_op_1 = FeatureOperation(
            operation_type=feat_op_1_dict["operation_type"],
            original_columns=feat_op_1_dict["original_columns"],
            derived_columns=feat_op_1_dict["derived_columns"],
            encoder=feat_op_1_dict["encoder"],
        )
        feat_op_2 = FeatureOperation(
            operation_type=feat_op_2_dict["operation_type"],
            original_columns=feat_op_2_dict["original_columns"],
            derived_columns=feat_op_2_dict["derived_columns"],
            encoder=feat_op_2_dict["encoder"],
        )

        are_feat_ops_equal = feat_op_1 == feat_op_2

        assert are_feat_ops_equal == is_equal_label

    def test_featureoperation_equals_with_different_instance_types(self):
        feat_op_1 = FeatureOperation(
            operation_type=OperationTypeEnum.BIN_SPLITTING,
            original_columns=("original_column_2",),
            derived_columns=("derived_column_1", "derived_column_2"),
            encoder=OneHotEncoder,
        )
        feat_op_2 = dict(
            operation_type=OperationTypeEnum.BIN_SPLITTING,
            original_columns=("original_column_2",),
            derived_columns=("derived_column_1", "derived_column_2"),
            encoder=OneHotEncoder,
        )

        are_feat_ops_equal = feat_op_1 == feat_op_2

        assert are_feat_ops_equal is False


@pytest.mark.parametrize(
    "series_type, expected_col_type_dict",
    [
        ("bool", {"col_name": "column_name", "col_type": "bool_col"}),
        ("string", {"col_name": "column_name", "col_type": "string_col"}),
        ("category", {"col_name": "column_name", "col_type": "string_col"}),
        ("float", {"col_name": "column_name", "col_type": "numerical_col"}),
        ("int", {"col_name": "column_name", "col_type": "numerical_col"}),
        ("float_int", {"col_name": "column_name", "col_type": "numerical_col"}),
        ("interval", {"col_name": "column_name", "col_type": "numerical_col"}),
        ("date", {"col_name": "column_name", "col_type": "other_col"}),
        ("mixed_0", {"col_name": "column_name", "col_type": "mixed_type_col"}),
        ("mixed_1", {"col_name": "column_name", "col_type": "mixed_type_col"}),
        ("mixed_2", {"col_name": "column_name", "col_type": "mixed_type_col"}),
    ],
)
def test_find_single_column_type(request, series_type, expected_col_type_dict):
    serie = SeriesMock.series_by_type(series_type)

    col_type_dict = _find_single_column_type(serie)

    assert col_type_dict == expected_col_type_dict, series_type


@pytest.mark.parametrize(
    "col_type, expected_column_single_type_set",
    [
        ("bool_col", {"bool_col_0", "bool_col_1"}),
        ("string_col", {"string_col_0", "string_col_1", "string_col_2"}),
        ("numerical_col", {"numerical_col_0"}),
        ("other_col", {"other_col_0"}),
        (
            "mixed_type_col",
            {
                "mixed_type_col_0",
                "mixed_type_col_1",
                "mixed_type_col_2",
                "mixed_type_col_3",
            },
        ),
    ],
)
def test_find_columns_by_type(request, col_type, expected_column_single_type_set):
    df_col_names_by_type = DataFrameMock.df_column_names_by_type()

    column_single_type_set = _find_samples_by_type(df_col_names_by_type, col_type)

    assert column_single_type_set == expected_column_single_type_set


def test_split_columns_by_type_parallel(request):
    df_by_type = DataFrameMock.df_multi_type()
    col_list = df_by_type.columns

    cols_by_type_tuple = _split_columns_by_type_parallel(df_by_type, col_list)

    assert cols_by_type_tuple == (
        {"mixed_type_col_0"},
        {"numerical_col_0", "interval_col_0"},
        {"string_col_0", "categorical_col_0"},
        {"bool_col_0"},
        {"datetime_col_0"},
    )
