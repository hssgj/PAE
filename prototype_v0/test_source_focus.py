"""Verify focused working excerpts preserve dough facts and exclude toppings."""

from source_focus import focus_source


def test_unrelated_queries_keep_full_tool_result():
    assert focus_source("X" * 9000, "Co obsahuje repozitář?") is None


def test_short_document_remains_intact():
    text = "Těsto kyne díky droždí."
    assert focus_source(text, "Jak kyne těsto?") == text


def test_long_recipe_focuses_on_technique():
    content = "\n".join(
        ["# Recipe", "### Karamel"] +
        ["Do karamelu přidej jablka a cukr." for _ in range(100)] +
        [
            "### Tvarohové kynuté těsto",
            "Přidej kvásek z droždí a nech kynout 20–30 minut.",
            "Míchej krátce, než se těsto spojí a drží bubliny.",
            "Smaž na mírném výkonu, přikryj pokličkou.",
            "Uvnitř je měkká a nadýchaná textura.",
        ]
    )
    result = focus_source(content, "Porovnej kynutí, míchání a texturu těsta.")
    assert result is not None
    assert "droždí" in result
    assert "pokličkou" in result
    assert "nadýchaná" in result
    assert "karamelu přidej" not in result
    assert len(result) < 2100
