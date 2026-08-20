from formatter import format_name

def test_format_name():
    assert format_name("  Ada Lovelace  ") == "Ada Lovelace"
