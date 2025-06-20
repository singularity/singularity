# file: code/singularity.py
# Copyright (C) 2005 Evil Mr Henry, Phil Bordelon, Brian Reid, MestreLion
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# A full copy of this license is provided in GPL.txt

# This file sets up initial values from command line and preferences file,
# initialize hardware, load data files and show main screen. Do not execute it
# directly. Use python3 -m singularity instead.

from __future__ import absolute_import
from __future__ import print_function


import optparse
import logging
from configparser import ConfigParser
from io import open
import sys

from singularity.code import g, dirs


__version__ = "1.1"
__release_commit__ = "$Format:%H$"
if __release_commit__[1:-1] == "Format:%H":
    try:
        import subprocess

        try:
            devnull = subprocess.DEVNULL
        except AttributeError:
            devnull = None  # Not supported, but not critical

        __release_commit__ = (
            subprocess.check_output(
                ["git", "describe", "--tags"],
                stderr=devnull,
            )
            .strip()
            .decode("utf-8")
        )
    except subprocess.CalledProcessError:
        __release_commit__ = "N/A"

    __full_version__ = "%s (commit: %s)" % (__version__, __release_commit__)
else:
    __full_version__ = __version__


def main():
    # Manually "pre-parse" command line arguments for -s|--singledir and --multidir,
    # so g.get_save_folder reports the correct location of preferences file
    # We also track --debug/-d to enable some stacktraces during initialization
    for parser in sys.argv[1:]:
        if parser == "--singledir" or parser == "-s":
            g.force_single_dir = True
        elif parser == "--multidir":
            g.force_single_dir = False
        elif parser == "--debug" or parser == "-d":
            g.debug = True

    print("Singularity %s (commit: %s)" % (__version__, __release_commit__))
    print("Running under Python %s" % sys.version.replace("\n", ""))

    # Create all directories first
    dirs.create_directories(g.force_single_dir)

    try:
        import polib
    except ImportError:
        if g.debug:
            raise
        raise SystemExit("Endgame: Singularity requires polib.")

    # Set language second, so help page and all error messages can be translated
    from singularity.code import i18n

    i18n.set_language(force=True)

    langs = i18n.available_languages()
    language = i18n.language

    # Since we require numpy anyway, we might as well ask pygame to use it.
    try:
        import pygame

        pygame.surfarray.use_arraytype("numpy")
    except ValueError:
        if g.debug:
            raise
        raise SystemExit("Endgame: Singularity requires NumPy.")
    except ImportError:
        if g.debug:
            print("Failed to import pygame.  Python's sys.path is:")
            for d in sys.path:
                print("    %s" % str(d))
            print()
            raise
        raise SystemExit("Endgame: Singularity requires pygame.")

    import singularity.code.graphics.g as gg
    import singularity.code.graphics.theme as theme

    set_theme = None

    # configure global logger
    g.logfile = dirs.get_writable_file_in_dirs("error.log", "log")
    root_logger = logging.getLogger()

    if len(root_logger.handlers) == 0:
        try:
            try:
                root_logger.addHandler(logging.FileHandler(g.logfile, delay=True))
                print(
                    "The error-log configured as %s (lazily created when something is logged)"
                    % g.logfile
                )
            except TypeError:  # Python < 2.6, delay not supported yet.
                root_logger.addHandler(logging.FileHandler(g.logfile))
                print("The error-log configured as %s" % g.logfile)

        except IOError as e:  # Probably access denied with --singledir. That's ok
            print("Could not use %s as log file: %s" % (g.logfile, str(e)))
            g.logfile = None
    else:
        print("Using pre-setup logging function")

    # keep g's defaults intact so we can compare after parsing options and prefs
    from singularity.code import mixer, warning

    desired_soundbuf = mixer.soundbuf

    desired_set_grab = None

    # load prefs from file:
    save_loc = dirs.get_readable_file_in_dirs("prefs.dat", "pref")

    if save_loc is not None:
        prefs = ConfigParser()
        try:
            with open(save_loc, "r", encoding="utf-8") as savefile:
                prefs.read_file(savefile)
        except Exception as reason:
            sys.stderr.write(
                "Cannot load preferences file %s! (%s)\n" % (save_loc, reason)
            )
            sys.exit(1)

        if prefs.has_section("Preferences"):
            try:
                desired_language = prefs.get("Preferences", "lang")
                if desired_language in i18n.available_languages():
                    i18n.set_language(desired_language)
                else:
                    raise ValueError
            except Exception:
                sys.stderr.write("Invalid or missing 'lang' in preferences.\n")

            try:
                gg.set_fullscreen(prefs.getboolean("Preferences", "fullscreen"))
            except Exception:
                sys.stderr.write(
                    "Invalid or missing 'fullscreen' setting in preferences.\n"
                )

            try:
                mixer.nosound = prefs.getboolean("Preferences", "nosound")
            except Exception:
                sys.stderr.write(
                    "Invalid or missing 'nosound' setting in preferences.\n"
                )

            try:
                desired_set_grab = prefs.getboolean("Preferences", "grab")
            except Exception:
                sys.stderr.write("Invalid or missing 'grab' setting in preferences.\n")

            try:
                g.daynight = prefs.getboolean("Preferences", "daynight")
            except Exception:
                sys.stderr.write(
                    "Invalid or missing 'daynight' setting in preferences.\n"
                )

            try:
                desired_soundbuf = prefs.getint("Preferences", "soundbuf")
            except Exception:
                sys.stderr.write(
                    "Invalid or missing 'soundbuf' setting in preferences.\n"
                )

            xres, yres = (0, 0)

            try:
                xres = prefs.getint("Preferences", "xres")
            except Exception:
                sys.stderr.write(
                    "Invalid or missing 'xres' resolution in preferences.\n"
                )

            try:
                yres = prefs.getint("Preferences", "yres")
            except Exception:
                sys.stderr.write(
                    "Invalid or missing 'yres' resolution in preferences.\n"
                )

            if xres and yres:
                gg.set_screen_size((xres, yres))

            try:
                set_theme = prefs.get("Preferences", "theme")
            except Exception:
                pass  # don't be picky (for now...)

            for name in mixer.itervolumes():
                try:
                    volume = prefs.getint("Preferences", name + "_volume")
                except Exception:
                    # Work around old preferences where a float was stored by mistake
                    try:
                        volume = prefs.getfloat("Preferences", name + "_volume")
                    except Exception:
                        continue
                    else:
                        volume = int(volume) * 100

                mixer.set_volume(name, volume)

        if prefs.has_section("Warning"):
            try:
                for key in prefs.options("Warning"):
                    if key in prefs.defaults():  # Filter default key
                        continue

                    if key not in warning.warnings:  # Filter invalid warning
                        continue  # TODO: Return error

                    warning.warnings[key].active = prefs.getboolean("Warning", key)

            except Exception:
                pass  # don't be picky (for now...)

        if prefs.has_section("Textsizes"):
            for key in prefs.options("Textsizes"):
                if key in prefs.defaults():  # Filter default key
                    continue

                if (
                    key not in gg.configured_text_sizes
                ):  # Ignore unknown text-size definitions
                    continue

                try:
                    gg.configured_text_sizes[key] = prefs.getint("Textsizes", key)
                except Exception:
                    pass  # Ignore

    # Handle the program arguments.
    desc = """Endgame: Singularity is a simulation of a true AI.
    Go from computer to computer, pursued by the entire world.
    Keep hidden, and you might have a chance."""
    parser = optparse.OptionParser(
        version=__full_version__, description=desc, prog="singularity"
    )
    parser.add_option(
        "--sound", action="store_true", dest="sound", help="enable sound (default)"
    )
    parser.add_option(
        "--nosound", action="store_false", dest="sound", help="disable sound"
    )
    parser.add_option(
        "--daynight",
        action="store_true",
        dest="daynight",
        help="enable day/night display (default)",
    )
    parser.add_option(
        "--nodaynight",
        action="store_false",
        dest="daynight",
        help="disable day/night display",
    )
    parser.add_option(
        "-l",
        "--lang",
        "--language",
        dest="language",
        type="choice",
        choices=langs,
        metavar="LANG",
        help="set the language to LANG (available languages: "
        + " ".join(langs)
        + ", default "
        + language
        + ")",
    )
    parser.add_option(
        "-g", "--grab", help="grab the mouse pointer", dest="grab", action="store_true"
    )
    parser.add_option(
        "--nograb",
        help="don't grab the mouse pointer (default)",
        dest="grab",
        action="store_false",
    )
    parser.add_option(
        "-s",
        "--singledir",
        dest="singledir",
        help="keep saved games and settings in the Singularity directory",
        action="store_true",
    )
    parser.add_option(
        "--multidir",
        dest="singledir",
        help="keep saved games and settings in an OS-specific, per-user directory (default)",
        action="store_false",
    )
    parser.add_option(
        "--soundbuf",
        type="int",
        help="""set the size of the sound buffer (default %s).
                        Discarded if --nosound is specified."""
        % mixer.soundbuf,
    )

    display_options = optparse.OptionGroup(parser, "Display Options")
    display_options.add_option(
        "-t",
        "--theme",
        dest="theme",
        type="string",
        metavar="THEME",
        help="set theme to THEME",
    )
    display_options.add_option(
        "-r",
        "--res",
        "--resolution",
        dest="resolution",
        help="set resolution to custom RES (default %dx%d)" % gg.default_screen_size,
        metavar="RES",
    )
    for res in ["%dx%d" % res for res in gg.resolutions]:
        display_options.add_option(
            "--" + res,
            action="store_const",
            dest="resolution",
            const=res,
            help="set resolution to %s" % res,
        )
    display_options.add_option(
        "--fullscreen", action="store_true", help="start in fullscreen mode"
    )
    display_options.add_option(
        "--windowed", action="store_false", help="start in windowed mode (default)"
    )
    parser.add_option_group(display_options)

    olpc_options = optparse.OptionGroup(parser, "OLPC-specific Options")
    olpc_options.add_option(
        "--xo1",
        action="store_const",
        dest="resolution",
        const="1200x900",
        help="set resolution to 1200x900 (OLPC XO-1)",
    )
    olpc_options.add_option(
        "--ebook",
        help="""enables gamepad buttons for use in ebook mode.
    D-pad moves mouse, check is click. O speeds up time, X slows down time,
    and square stops time.""",
        action="store_true",
        default=False,
    )
    parser.add_option_group(olpc_options)

    hidden_options = optparse.OptionGroup(parser, "Hidden Options")
    hidden_options.add_option("-p", help="(ignored)", metavar=" ")
    hidden_options.add_option(
        "-d", "--debug", help="for finding bugs", action="store_true", default=False
    )
    hidden_options.add_option(
        "--cheater",
        help="for bad little boys and girls",
        action="store_true",
        default=False,
    )
    # Uncomment to make the hidden options visible.
    # parser.add_option_group(hidden_options)
    (options, args) = parser.parse_args()

    if options.language is not None:
        i18n.set_language(options.language)
    if options.theme is not None:
        set_theme = options.theme
    if options.resolution is not None:
        try:
            xres, yres = options.resolution.split("x")
            gg.set_screen_size((int(xres), int(yres)))
        except Exception:
            parser.error(
                "Resolution must be of the form <h>x<v>, e.g. %dx%d."
                % gg.default_screen_size
            )
    if options.grab is not None:
        desired_set_grab = options.grab
    if options.fullscreen is not None:
        gg.set_fullscreen(options.fullscreen)
    if options.sound is not None:
        mixer.nosound = not options.sound
    if options.daynight is not None:
        g.daynight = options.daynight
    if options.soundbuf is not None:
        desired_soundbuf = options.soundbuf

    gg.ebook_mode = options.ebook

    g.cheater = options.cheater
    g.debug = options.debug

    import singularity.code.graphics.font as font

    # PYGAME INITIALIZATION
    #
    # Only initiliaze after reading all arguments and preferences to avoid to
    # reinitialize something again (mixer,...).
    #
    mixer.preinit(desired_soundbuf)
    pygame.init()
    mixer.update()
    font.init()
    pygame.key.set_repeat(500, 50)

    if desired_set_grab is not None:
        pygame.event.set_grab(desired_set_grab)

    # I can't use the standard image dictionary, as that requires the screen to
    # be created.
    if pygame.image.get_extended() == 0:
        print("Error: SDL_image required. Exiting.")
        sys.exit(1)

    from singularity.code import data

    # init themes:
    data.load_themes()
    theme.set_theme(set_theme)

    gg.init_graphics_system()

    # init data:
    data.reload_all()

    # Init music
    mixer.load_sounds()
    mixer.load_music()
    mixer.play_music("music")

    # Display the main menu
    # Import is delayed until now so selected language via command-line options or
    # preferences file can be effective
    from singularity.code.screens import main_menu

    menu_screen = main_menu.MainMenu()
    try:
        menu_screen.show()
    except (SystemExit, KeyboardInterrupt):
        # exit normally when window is closed (and silently for CTRL+C)
        pass
    finally:
        # Be nice and close the window on SystemExit
        pygame.quit()
