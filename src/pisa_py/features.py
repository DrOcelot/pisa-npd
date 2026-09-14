"""Derived variables built on top of the committed subset."""

import polars as pl

from pisa_py.io import PV_COLS

GENDER = "ST004D01T"
DECILE_LABELS = [f"D{i + 1}" for i in range(10)]


def with_mean_score(frame: pl.LazyFrame) -> pl.LazyFrame:
    """Average every plausible value into a single `mean_score` column.

    The thirty plausible values are dropped afterwards, since nothing
    downstream needs them once the mean is taken.
    """
    return frame.with_columns(pl.mean_horizontal(PV_COLS).alias("mean_score")).drop(PV_COLS)


def with_gender_ability_group(frame: pl.LazyFrame, gender: str = GENDER) -> pl.LazyFrame:
    """Label each pupil by gender and whether they sit in the lowest decile.

    Adds `mean_score`, `decile` and `gender_ability_group`. Deciles are cut
    within gender, so `D1` means the lowest tenth of that gender rather than
    the lowest tenth overall. Pupils with no recorded gender cannot be placed
    in a group and are labelled `excluded`.

    Returns:
        The frame with `gender_ability_group` values such as `LA_Male`
        (low ability) and `rest_Female`.
    """
    scored = with_mean_score(frame).with_columns(
        pl.col("mean_score")
        .qcut(10, labels=DECILE_LABELS)
        .alias("decile")
        .over(gender)
    )
    name = pl.col(gender).cast(pl.String)
    return scored.with_columns(
        pl.when(name.is_null())
        .then(pl.lit("excluded"))
        .when(pl.col("decile") == "D1")
        .then(pl.concat_str(pl.lit("LA_"), name))
        .otherwise(pl.concat_str(pl.lit("rest_"), name))
        .alias("gender_ability_group")
    )


def percentage_by_group(
    frame: pl.LazyFrame,
    factor: str,
    group: str = "gender_ability_group",
) -> pl.DataFrame:
    """Share of each group giving each answer to `factor`, as a percentage.

    Percentages run within `group`, so the values for one gender-ability
    group sum to 100 across the factor's categories.
    """
    return (
        frame.group_by([factor, group])
        .agg(pl.len().alias("n"))
        .with_columns((pl.col("n") / pl.col("n").sum().over(group) * 100).alias("pct"))
        .collect()
    )
