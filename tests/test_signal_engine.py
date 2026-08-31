"""Toetst de signaal-engine tegen de classificatieregel uit FO hoofdstuk 5.
De fase-0-validatieset (10-15 handmatig ingeschatte advertenties) hoort hier
als extra cases bij zodra die er is — zie TO hoofdstuk 10."""

import pytest

from signal_engine import LONGEVITY_THRESHOLD_DAYS, VARIANT_THRESHOLD, classify


@pytest.mark.parametrize(
    "longevity, variants, verwacht",
    [
        (60, 5, "strong"),
        (45, 3, "strong"),
        (60, 1, "mid"),
        (10, 5, "mid"),
        (44, 2, "weak"),
        (0, 0, "weak"),
    ],
)
def test_classify(longevity, variants, verwacht):
    assert classify(longevity, variants) == verwacht


def test_drempels_op_de_grens():
    assert classify(LONGEVITY_THRESHOLD_DAYS - 1, VARIANT_THRESHOLD) == "mid"
    assert classify(LONGEVITY_THRESHOLD_DAYS, VARIANT_THRESHOLD - 1) == "mid"
