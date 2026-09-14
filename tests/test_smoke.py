"""Checks that the package imports and the committed subset is intact.

The subset assertions are skipped when the parquet is absent, so the suite
still passes on a clone where `git lfs pull` has not been run.
"""

import polars as pl
import pytest

from pisa_py.features import with_gender_ability_group
from pisa_py.io import CORE_COLS, PV_COLS, SUBSET_PARQUET, load_subset, subset_columns


def test_subset_columns_are_unique() -> None:
    columns = subset_columns()
    assert len(columns) == len(set(columns))
    assert set(CORE_COLS) <= set(columns)


def test_plausible_values_are_complete() -> None:
    assert len(PV_COLS) == 30
    for domain in ("MATH", "READ", "SCIE"):
        assert sum(column.endswith(domain) for column in PV_COLS) == 10


@pytest.mark.skipif(not SUBSET_PARQUET.exists(), reason="subset not fetched from LFS")
def test_subset_matches_the_declared_columns() -> None:
    assert load_subset().collect_schema().names() == subset_columns()


@pytest.mark.skipif(not SUBSET_PARQUET.exists(), reason="subset not fetched from LFS")
def test_gender_ability_group_labels_every_pupil() -> None:
    groups = (
        with_gender_ability_group(load_subset())
        .select(pl.col("gender_ability_group"))
        .collect()
        .to_series()
    )
    assert groups.null_count() == 0
    assert {"LA_Male", "LA_Female", "rest_Male", "rest_Female"} <= set(groups.unique())
