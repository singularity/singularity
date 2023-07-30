from singularity.code.graphics.dialog import Dialog

from singularity.code.graphics import g as gg


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
