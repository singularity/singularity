import pytest

from singularity.code import g


@pytest.mark.parametrize(
    "input_text,hotkey_chars,cleaned_text",
    [
        ("E&XIT", "x", "EXIT"),
        ("&Play D&&D", "p", "Play D&D"),
        ("Romeo & &Juliet", "j", "Romeo & Juliet"),
        ("Trailing&", "", "Trailing&"),
        ("&Multiple&Keys", "mk", "MultipleKeys"),
        ("M&&&M", "m", "M&M"),
    ],
)
def test_hotkeys(input_text, hotkey_chars, cleaned_text):
    hotkey_data = g.hotkey(input_text)
    actual_hotkey_chars = "".join(x[0] for x in hotkey_data["keys"])
    actual_cleaned_text = hotkey_data["text"]
    actual_hotkey_char = hotkey_data["key"][0] if hotkey_data["key"] else ""
    expected_hotkey = hotkey_chars[0] if hotkey_chars else ""

    print(("input: %s - %s" % (input_text, str(hotkey_data["keys"]))))
    assert actual_hotkey_chars == hotkey_chars
    assert actual_cleaned_text == cleaned_text
    assert actual_hotkey_char == expected_hotkey


def test_hotkey_matcher_ctrl_modifier():
    """Test that HotKeyMatcher correctly handles CTRL modifier."""
    import pygame
    from singularity.code.global_hotkeys import HotKeyMatcher

    matcher = HotKeyMatcher()

    def dummy_action():
        pass

    # Ctrl+S should be addable
    matcher.add_hotkey(pygame.K_s, pygame.KMOD_CTRL, dummy_action)
    assert pygame.K_s in matcher._hotkeys

    # Plain 's' without modifier should NOT return the hotkey action
    class MockEvent:
        type = pygame.KEYDOWN
        key = pygame.K_s

    pygame.key.get_mods = lambda: 0
    result = matcher.detect_hotkey(MockEvent())
    assert result is None

    # Ctrl+S should return the hotkey action (game loop invokes it, not detect_hotkey)
    pygame.key.get_mods = lambda: pygame.KMOD_CTRL
    result = matcher.detect_hotkey(MockEvent())
    assert result is dummy_action
