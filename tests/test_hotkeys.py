import pytest

from code import g


@pytest.mark.parametrize("input_text,hotkey_chars,cleaned_text", [
    ("E&XIT", 'x', 'EXIT'),
    ("&Play D&&D", 'p', 'Play D&D'),
    ("Romeo & &Juliet", 'j', 'Romeo & Juliet'),
    ("Trailing&", '', 'Trailing&'),
    ("&Multiple&Keys", 'mk', 'MultipleKeys'),
    ('M&&&M', 'm', 'M&M'),
])
def test_hotkeys(input_text, hotkey_chars, cleaned_text):
    hotkey_data = g.hotkey(input_text)
    actual_hotkey_chars = ''.join(x[0] for x in hotkey_data['keys'])
    actual_cleaned_text = hotkey_data['text']
    actual_hotkey_char = hotkey_data['key'][0] if hotkey_data['key'] else ''
    expected_hotkey = hotkey_chars[0] if hotkey_chars else ''

    print(("input: %s - %s" % (input_text, str(hotkey_data['keys']))))
    assert actual_hotkey_chars == hotkey_chars
    assert actual_cleaned_text == cleaned_text
    assert actual_hotkey_char == expected_hotkey
   
