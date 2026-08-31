import pytest

from i18n import DEFAULT_LANG, LANGUAGES, TRANSLATIONS, t


def test_alle_talen_hebben_dezelfde_sleutels():
    basis = set(TRANSLATIONS[DEFAULT_LANG])
    for lang, vertaling in TRANSLATIONS.items():
        assert set(vertaling) == basis, f"{lang} wijkt af: {basis ^ set(vertaling)}"


def test_elke_taal_in_languages_heeft_vertalingen():
    assert set(LANGUAGES) == set(TRANSLATIONS)


@pytest.mark.parametrize("lang", list(TRANSLATIONS))
def test_geen_lege_waarden(lang):
    leeg = [k for k, v in TRANSLATIONS[lang].items() if not v.strip()]
    assert not leeg, f"{lang} heeft lege waarden: {leeg}"


def test_onbekende_sleutel_valt_terug_op_de_sleutel_zelf():
    assert t("bestaat.niet", "nl") == "bestaat.niet"


def test_onbekende_taal_valt_terug_op_default():
    assert t("nav.feed", "de") == TRANSLATIONS[DEFAULT_LANG]["nav.feed"]
