from unittest import TestCase

from semantic_model_generator.data_processing.cte_utils import (
    context_to_column_format,
    generate_agg_expr_selects,
    generate_select,
    is_aggregation_expr,
)
from semantic_model_generator.protos import semantic_model_pb2


def get_test_ctx() -> semantic_model_pb2.SemanticModel:
    return semantic_model_pb2.SemanticModel(
        name="test_ctx",
        tables=[
            semantic_model_pb2.Table(
                name="t1",
                dimensions=[
                    semantic_model_pb2.Dimension(
                        name="d1",
                        description="d1_description",
                        synonyms=["d1_synonym1", "d1_synonym2"],
                        expr="d1_expr",
                        data_type="d1_data_type",
                        unique=True,
                        sample_values=["d1_sample_value1", "d1_sample_value2"],
                    ),
                    semantic_model_pb2.Dimension(
                        name="d2",
                        description="d2_description",
                        expr="d2_expr",
                    ),
                ],
            ),
            semantic_model_pb2.Table(
                name="t2",
                time_dimensions=[
                    semantic_model_pb2.TimeDimension(
                        name="td1",
                        description="td1_description",
                        synonyms=["td1_synonym1", "td1_synonym2"],
                        expr="td1_expr",
                        data_type="td1_data_type",
                        unique=True,
                        sample_values=["td1_sample_value1", "td1_sample_value2"],
                    ),
                ],
                measures=[
                    semantic_model_pb2.Measure(
                        name="m1",
                        description="m1_description",
                        synonyms=["m1_synonym1", "m1_synonym2"],
                        expr="m1_expr",
                        data_type="m1_data_type",
                        default_aggregation=semantic_model_pb2.AggregationType.avg,
                        sample_values=["m1_sample_value1", "m1_sample_value2"],
                    ),
                    semantic_model_pb2.Measure(
                        name="m2",
                        description="m1_description",
                        expr="m1_expr",
                    ),
                ],
            ),
        ],
    )


def get_test_ctx_col_format() -> semantic_model_pb2.SemanticModel:
    return semantic_model_pb2.SemanticModel(
        name="test_ctx",
        tables=[
            semantic_model_pb2.Table(
                name="t1",
                columns=[
                    semantic_model_pb2.Column(
                        name="d1",
                        kind=semantic_model_pb2.ColumnKind.dimension,
                        description="d1_description",
                        synonyms=["d1_synonym1", "d1_synonym2"],
                        expr="d1_expr",
                        data_type="d1_data_type",
                        unique=True,
                        sample_values=["d1_sample_value1", "d1_sample_value2"],
                    ),
                    semantic_model_pb2.Column(
                        name="d2",
                        kind=semantic_model_pb2.ColumnKind.dimension,
                        description="d2_description",
                        expr="d2_expr",
                    ),
                ],
            ),
            semantic_model_pb2.Table(
                name="t2",
                columns=[
                    semantic_model_pb2.Column(
                        name="td1",
                        kind=semantic_model_pb2.ColumnKind.time_dimension,
                        description="td1_description",
                        synonyms=["td1_synonym1", "td1_synonym2"],
                        expr="td1_expr",
                        data_type="td1_data_type",
                        unique=True,
                        sample_values=["td1_sample_value1", "td1_sample_value2"],
                    ),
                    semantic_model_pb2.Column(
                        name="m1",
                        kind=semantic_model_pb2.ColumnKind.measure,
                        description="m1_description",
                        synonyms=["m1_synonym1", "m1_synonym2"],
                        expr="m1_expr",
                        data_type="m1_data_type",
                        default_aggregation=semantic_model_pb2.AggregationType.avg,
                        sample_values=["m1_sample_value1", "m1_sample_value2"],
                    ),
                    semantic_model_pb2.Column(
                        name="m2",
                        kind=semantic_model_pb2.ColumnKind.measure,
                        description="m1_description",
                        expr="m1_expr",
                    ),
                ],
            ),
        ],
    )


def get_test_table_col_format() -> semantic_model_pb2.Table:
    return semantic_model_pb2.Table(
        name="t1",
        base_table=semantic_model_pb2.FullyQualifiedTable(
            database="db", schema="sc", table="t1"
        ),
        columns=[
            semantic_model_pb2.Column(
                name="d1",
                kind=semantic_model_pb2.ColumnKind.dimension,
                description="d1_description",
                synonyms=["d1_synonym1", "d1_synonym2"],
                expr="d1_expr",
                data_type="d1_data_type",
                unique=True,
                sample_values=["d1_sample_value1", "d1_sample_value2"],
            ),
            semantic_model_pb2.Column(
                name="d2",
                kind=semantic_model_pb2.ColumnKind.dimension,
                description="d2_description",
                expr="d2_expr",
            ),
        ],
    )


def get_test_table_col_format_w_agg() -> semantic_model_pb2.Table:
    return semantic_model_pb2.Table(
        name="t1",
        base_table=semantic_model_pb2.FullyQualifiedTable(
            database="db", schema="sc", table="t1"
        ),
        columns=[
            semantic_model_pb2.Column(
                name="d1",
                kind=semantic_model_pb2.ColumnKind.dimension,
                description="d1_description",
                synonyms=["d1_synonym1", "d1_synonym2"],
                expr="d1_expr",
                data_type="d1_data_type",
                unique=True,
                sample_values=["d1_sample_value1", "d1_sample_value2"],
            ),
            semantic_model_pb2.Column(
                name="d2",
                kind=semantic_model_pb2.ColumnKind.measure,
                description="d2_description",
                expr="sum(d2)",
            ),
            semantic_model_pb2.Column(
                name="d3",
                kind=semantic_model_pb2.ColumnKind.measure,
                description="d3_description",
                expr="sum(d3) over (partition by d1)",
            ),
        ],
    )


class SemanticModelTest(TestCase):
    def test_convert_to_column_format(self) -> None:
        """
        Verifies that Dimension/time_dimension/measure are appropriately
        converted into corresponding columns.
        """
        ctx = get_test_ctx()
        want = get_test_ctx_col_format()
        got = context_to_column_format(ctx)
        self.assertEqual(want, got)

    def test_convert_to_column_format_noop(self) -> None:
        """
        Verify that context_to_column_format() is a no-op if the context is already
        in column format.
        """
        # A context already in column format.
        ctx = get_test_ctx_col_format()
        got = context_to_column_format(ctx)
        self.assertEqual(ctx, got)

    def test_is_aggregation_expr(self) -> None:
        for col, want in [
            (semantic_model_pb2.Column(expr="foo", kind="measure"), False),
            (semantic_model_pb2.Column(expr="sum(foo)", kind="measure"), True),
            (
                semantic_model_pb2.Column(expr="sum(foo)/sum(bar)", kind="measure"),
                True,
            ),
            (semantic_model_pb2.Column(expr="avg(foo)", kind="measure"), True),
            (semantic_model_pb2.Column(expr="foo + bar", kind="measure"), False),
            (
                semantic_model_pb2.Column(
                    expr="sum(foo) over (partition by bar)", kind="measure"
                ),
                False,
            ),
        ]:
            with self.subTest():
                self.assertEqual(is_aggregation_expr(col), want)

    def test_generate_select(self) -> None:
        col_format_tbl = get_test_table_col_format()
        got = generate_select(col_format_tbl, 100)
        want = "WITH __t1 AS (SELECT d1_expr AS d1, d2_expr AS d2 FROM db.sc.t1) SELECT * FROM __t1 LIMIT 100"
        assert got == want

    def test_generate_select_w_agg(self) -> None:
        col_format_tbl = get_test_table_col_format_w_agg()
        got = generate_select(col_format_tbl, 100)
        want = "WITH __t1 AS (SELECT d1_expr AS d1, SUM(d3) OVER (PARTITION BY d1) AS d3 FROM db.sc.t1) SELECT * FROM __t1 LIMIT 100"
        assert got == want

        agg_got = generate_agg_expr_selects(col_format_tbl, 100)
        agg_want = ["SELECT SUM(d2) AS d2 FROM db.sc.t1 LIMIT 100"]
        assert agg_got == agg_want
