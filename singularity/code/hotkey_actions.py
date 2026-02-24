import operator


from singularity.code import g

from singularity.code.graphics.dialog import Dialog

from singularity.code.graphics import g as gg, dialog, constants
from singularity.code.savegame import (
    QUICKSAVE_NAME,
    create_savegame,
    get_savegames,
    load_savegame,
)


def toggle_fullscreen():
    gg.set_fullscreen(not gg.fullscreen)
    Dialog.top.needs_resize = True


def reload_theme():
    import singularity.code.graphics.theme as theme

    if theme.current:
        import singularity.code.data as data

        theme_id = theme.current.id
        data.load_themes()
        theme.set_theme(theme_id, force_reload=True)


def quicksave():
    from singularity.code.screens.map import MapScreen

    if g.is_game_running():
        create_savegame(QUICKSAVE_NAME)
        if isinstance(Dialog.current_dialog, MapScreen):
            Dialog.current_dialog.show_notification(_("Quicksave complete!"))
            print("quicksave")

def quickload():
    from singularity.code.screens.map import MapScreen

    if not g.is_game_running():
        return
    map_screen = Dialog.current_dialog
    # We only allow quickloads from the MapScreen.  If you load from a submenu, the menu might
    # not be updated (or even available - e.g., if you are viewing a base). To avoid corrupt
    # state, limit quickload to map screen, where we know we can easily recover.
    if not isinstance(map_screen, MapScreen):
        return
    quicksaves = [s for s in get_savegames() if s.name == QUICKSAVE_NAME]
    if not quicksaves:
        return
    msg = _("Load quicksave? Any unsaved progress will be lost.")
    yn = dialog.YesNoDialog(
        map_screen,
        pos=(-0.5, -0.5),
        size=(-0.3, -0.3),
        anchor=constants.MID_CENTER,
        text=msg,
    )
    go_ahead = dialog.call_dialog(yn, map_screen)
    yn.parent = None
    if not go_ahead:
        return
    save = max(quicksaves, key=operator.attrgetter("mtime"))
    load_savegame(save)
    Dialog.top.needs_reconfig = True
    Dialog.top.needs_rebuild = True


def toggle_cheat_menu():
    from singularity.code.screens.map import MapScreen
    if not g.is_game_running():
        return
    map_screen = Dialog.current_dialog
    # We only allow enabling cheats on the MapScreen (that is the only place the menu is enabled anyway
    if not isinstance(map_screen, MapScreen):
        return
    g.cheater = not g.cheater
    if g.cheater:
        print("Cheat menu enabled!")
    else:
        print("Cheat menu disabled")

    map_screen.cheat_button.visible = g.cheater
    map_screen.cheat_button.enabled = g.cheater
    map_screen.needs_reconfig = True
