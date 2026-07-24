"""
TASK-012 tests for strip_html() Unicode zero-width / control cleanup.

Run with: python tests/test_strip_html.py
"""

import sys
import os

# Add project root to sys.path so we can import `app.imap_client`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.imap_client import strip_html  # noqa: E402


# === Tests for NEW TASK-012 functionality (Unicode zero-width cleanup) ===

def test_zwsp_between_words():
    """Кейс 1: U+200B (ZWSP) между словами удаляется."""
    text = "hello\u200bworld"
    result = strip_html(text)
    assert "\u200b" not in result, f"U+200B остался: {result!r}"
    assert "hello" in result and "world" in result


def test_braille_blank_stripped():
    """Кейс 2: 200× U+2800 (Braille Pattern Blank) — длинная строка из мусора."""
    garbage = "\u2800" * 200
    result = strip_html(garbage)
    assert "\u2800" not in result, f"U+2800 остался: {result!r}"
    assert result == ""


def test_bom_stripped():
    """Кейс 3: U+FEFF (BOM) в начале."""
    text = "\ufeffHello"
    result = strip_html(text)
    assert result == "Hello", f"Expected 'Hello', got {result!r}"


def test_dedup_invisible_similar_lines():
    """Кейс 4: ZWJ — строки 'X\\u2800' и 'X' считаются дублями после очистки."""
    text = "X\u2800\nX\nY"
    result = strip_html(text)
    assert result.count("X") == 1, f"Дубликат не схлопнулся: {result!r}"
    assert "Y" in result


def test_real_garbage_case():
    """Кейс 5: реальный кейс из TEST-REPORT-010 (UID 84284, roycenter.co.il)."""
    real_garbage = (
        "Одна история с ретрита \u200c\u200c\u200c \u2800 \u2800 \u2800 \u2800 \u2800 \u2800 \u2800 \u2800\n"
        + ("\u200b" * 100)
        + ("\u034f" * 50)
        + ("\u2800" * 300)
    )
    result = strip_html(real_garbage)
    for code_point, name in [
        (0x200B, "ZWSP"),
        (0x200C, "ZWNJ"),
        (0x200D, "ZWJ"),
        (0x2007, "Figure Space"),
        (0x034F, "CGJ"),
        (0x2800, "Braille Blank"),
        (0xFEFF, "BOM"),
    ]:
        assert chr(code_point) not in result, f"U+{code_point:04X} ({name}) остался"
    assert "Одна история с ретрита" in result
    assert len(result) < 100, f"Слишком длинный результат ({len(result)} chars)"


def test_zwj_stripped():
    """Бонус: U+200D (ZWJ) удаляется."""
    text = "test\u200dtext"
    result = strip_html(text)
    assert "\u200d" not in result


def test_figure_space_stripped():
    """Бонус: U+2007 (Figure Space) удаляется."""
    text = "test\u2007text"
    result = strip_html(text)
    assert "\u2007" not in result


def test_cgj_stripped():
    """Бонус: U+034F (CGJ) удаляется."""
    text = "test\u034ftext"
    result = strip_html(text)
    assert "\u034f" not in result


def test_en_quad_stripped():
    """Бонус: U+2000 (En Quad) удаляется."""
    text = "test\u2000text"
    result = strip_html(text)
    assert "\u2000" not in result


def test_hair_space_stripped():
    """Бонус: U+200A (Hair Space) удаляется."""
    text = "test\u200atext"
    result = strip_html(text)
    assert "\u200a" not in result


def test_empty_string():
    """Бонус: пустая строка и None."""
    assert strip_html("") == ""
    assert strip_html(None) == ""


# === Backward-compat tests (existing behavior must NOT break) ===

def test_bc_html_tags_removed():
    """BC-1: HTML-теги удаляются."""
    html = '<html><body><p>Hello <b>world</b></p></body></html>'
    r = strip_html(html)
    assert '<' not in r and 'Hello' in r and 'world' in r


def test_bc_html_entities_decoded():
    """BC-2: HTML-entities декодируются (&lt;, &gt;, &amp;, &nbsp;)."""
    e = '&nbsp;hello&nbsp;&amp;world&lt;tag&gt;'
    r = strip_html(e)
    assert '&lt;' not in r and '&gt;' not in r
    assert '&amp;' not in r and '&nbsp;' not in r
    assert 'hello' in r and 'world' in r


def test_bc_whitespace_normalized():
    """BC-3: множественные пробелы/табы → один пробел."""
    ws = 'a  b\t\tc\n\n\n\n\nd'
    r = strip_html(ws)
    assert 'a b c' in r and r.endswith('d')


def test_bc_artifact_96_removed():
    """BC-4: изолированное число в начале (1-999) удаляется."""
    art = '96\nРеальный текст'
    r = strip_html(art)
    assert not r.startswith('96')


def test_bc_multi_blank_collapsed():
    """BC-5: тройные+ пустые строки схлопываются; одна пустая — сохраняется."""
    mb = 'line1\n\n\n\n\nline2'
    r = strip_html(mb)
    assert '\n\n\n' not in r, f"Тройная пустая строка осталась: {r!r}"
    assert 'line1' in r and 'line2' in r


def test_bc_dedup_identical_lines():
    """BC-6: повторяющиеся строки дедуплицируются."""
    dup = 'X\nX\nX\nY'
    r = strip_html(dup)
    assert r.count('X') == 1 and 'Y' in r


def test_bc_zwnj_entity_removed():
    """BC-7: HTML-entity &zwnj; удаляется."""
    z = 'before&zwnj;after'
    r = strip_html(z)
    assert 'zwnj' not in r and 'before' in r and 'after' in r


def test_bc_clean_text_untouched():
    """BC-8: чистый текст без HTML/мусора не трогается."""
    clean = 'Просто нормальный текст письма без всякой ерунды'
    r = strip_html(clean)
    assert r == clean


def test_bc_cyrillic_latin_preserved():
    """BC-9: кириллица + латиница сохраняются."""
    mix = 'Subject: Важное письмо от John Smith\nТекст сообщения'
    r = strip_html(mix)
    assert 'Важное' in r and 'John Smith' in r


def test_bc_multi_paragraph():
    """BC-10: многоабзацный текст сохраняет структуру."""
    multi = 'Para 1\n\nPara 2\n\nPara 3'
    r = strip_html(multi)
    assert r.count('Para') == 3


# === Test runner ===

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith(("test_", "test_bc_")) and callable(v)]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"  {t.__name__}: OK")
            passed += 1
        except AssertionError as e:
            print(f"  {t.__name__}: FAIL — {e}")
            failed += 1
        except Exception as e:
            print(f"  {t.__name__}: ERROR — {type(e).__name__}: {e}")
            failed += 1
    print()
    print(f"=== {passed} passed, {failed} failed (out of {len(tests)}) ===")
    sys.exit(0 if failed == 0 else 1)
