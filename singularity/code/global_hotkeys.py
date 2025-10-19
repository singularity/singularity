import dataclasses
from typing import Callable, Optional

import pygame

HotkeyAction = Callable[[], None]


_MODIFIERLESS_HOT_KEYS = frozenset(
    {
        pygame.K_F1,
        pygame.K_F2,
        pygame.K_F3,
        pygame.K_F4,
        pygame.K_F5,
        pygame.K_F6,
        pygame.K_F7,
        pygame.K_F8,
        pygame.K_F9,
    }
)


@dataclasses.dataclass
class GlobalHotKey:
    modifiers: int
    key: int
    action: HotkeyAction


class HotKeyMatcher:
    _hotkeys = {}

    def detect_hotkey(self, event: pygame.event) -> Optional[HotkeyAction]:
        if event.type != pygame.KEYDOWN:
            return None
        hk = self._hotkeys.get(event.key)
        if hk is None:
            return None
        if hk.modifiers != 0 and not (pygame.key.get_mods() & hk.modifiers):
            return None
        return hk.action

    def clear_hotkeys(self) -> None:
        self._hotkeys.clear()

    def add_hotkey(self, key: int, hotkey_modifiers: int, action: HotkeyAction) -> None:
        if hotkey_modifiers not in (0, pygame.KMOD_ALT):
            # Limitation in implementation, feel free to fix to code to support other modifiers. Will require
            # a data structure change (ALT + ENTER vs. CTRL + ENTER vs. CTRL + ALT + ENTER) and an up todate to
            # detect_hotkey
            raise ValueError("Only ALT is supported as a global hotkey modifier")
        if hotkey_modifiers == 0 ^ key in _MODIFIERLESS_HOT_KEYS:
            name = pygame.key.name(key)
            if hotkey_modifiers == 0:
                # The lack of modifier is a problem for generic keys such as "ENTER" or "A" because those are
                # often "dialog" level hotkeys. Therefore, we require most global hotkeys to have a modifier.
                raise ValueError(
                    f'The key "{name}" when used as global hotkey must have modifiers (e.g., "ALT + {name}")'
                )
            raise ValueError(f'The hotkey "{name}" cannot use modifiers')
        ghk = GlobalHotKey(key=key, modifiers=hotkey_modifiers, action=action)
        if ghk.key in self._hotkeys:
            raise ValueError(f'The "{key}" is already in use as a hotkey')
        self._hotkeys[ghk.key] = ghk


_ACTIVE_HOTKEYS: Optional[HotKeyMatcher] = None


def _active_hotkeys() -> HotKeyMatcher:
    global _ACTIVE_HOTKEYS
    if _ACTIVE_HOTKEYS is None:
        _ACTIVE_HOTKEYS = HotKeyMatcher()
        reset_hotkeys()
    return _ACTIVE_HOTKEYS


def reset_hotkeys():
    _active_hotkeys().clear_hotkeys()
    import singularity.code.hotkey_actions as hka

    # FIXME: Make these configurable
    add_hotkey(pygame.K_RETURN, hka.toggle_fullscreen, hotkey_modifiers=pygame.KMOD_ALT)
    add_hotkey(pygame.K_F5, hka.quicksave)
    add_hotkey(pygame.K_F6, hka.reload_theme)
    add_hotkey(pygame.K_F9, hka.quickload)
    add_hotkey(pygame.K_F11, hka.toggle_cheat_menu)


def add_hotkey(key: int, action: HotkeyAction, *, hotkey_modifiers: int = 0) -> None:
    _active_hotkeys().add_hotkey(key, hotkey_modifiers, action)


def detect_global_hotkey(event: pygame.event) -> Optional[HotkeyAction]:
    return _active_hotkeys().detect_hotkey(event)


def key_from_name(name: str) -> int:
    return pygame.key.key_code(name.lower())

def modifier_from_name(name: Optional[str]) -> int:
    #for now only ctrl can be used for modifier - it is just for future
    if name is None:
        return 0
    name = name.upper()
    if name == "ALT":
        return pygame.KMOD_ALT
    elif name == "CTRL":
        return pygame.KMOD_CTRL
    elif name == "SHIFT":
        return pygame.KMOD_SHIFT
    return 0  # pre neznáme alebo None

import json
from pathlib import Path

def load_hotkey_config(config_path: Path, actions_module) -> None:
    _active_hotkeys().clear_hotkeys()

    with open(config_path, "r") as f:
        data = json.load(f)

    for action_name, cfg in data.items():
        key = key_from_name(cfg["key"])
        mod = modifier_from_name(cfg.get("modifier"))
        action = getattr(actions_module, action_name, None)
        if action is None:
            print(f"[Warning] Action '{action_name}' not found in hotkey_actions")
            continue
        add_hotkey(key, action, hotkey_modifiers=mod)

