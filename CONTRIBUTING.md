# Contributing to Endgame: Singularity

We welcome contributions for everything - including this possibly
incomplete document.  :)

Notable, you can help us even without being able to code:

 * Translations! See the dedicated section on translations below
 * UI themes
 * Testing and filing bugs (#38, #115, #206, #207, #208 and many more)
 * Submitting improvement requests (#19, #64, #83)

Examples of past pull requests/patches that did not require code skills:

 * We were looking for a new UI theme (#71) and got the `Nightmode` UI theme (#119)
 * We needed help finding a new click sound (#201) and got one (#210)
 * All our existing translations

## Discussion fora
Some of the developers are available in the following IRC room:

 * IRC Room: #singularity on irc.oftc.net (port 6667)

Please note that there may be a significant delay between messages here
depending on your time zone and availability of the members in the channel.
Therefore, we encourage you to ask your question and have patience until we
are back.

## License assumption of work provided

We assume that all submissions are under the same license as the
content being changed unless explicitly stated otherwise in the
submission or content.  For new content, the license is assumed
to the the default license of that content if not explicitly
stated to be under another license.

Please see `LICENSE.txt` for details about the license terms.

If you wish to submit work under a different license, please get in
contact with us before starting the work.  Unfortunately, we may have
to reject work that is not under a license compatible with the project
licenses or the project goals.

## Translations

### Updating existing translations

Please have a look at the .po files in the directory
`singularity/i18n/lang_<ll_CC>` where `<ll_CC>` is the language code
for your language (e.g. `fr_FR` or `pt_BR`).

You can refresh the translations by using the command:

     utils/gettext-singularity --catalog <messages|data_str|story>

The `--catalog` parameter determines whether the `messages.po`, `data_str.po`,
or the `story.po` file will be refreshed and checked.

### Adding translations for a new language

You can add translations for a new language by running:

    utils/gettext-singularity --catalog <messages|data_str|story> --new <lang_code>

It will prompt you for a few details (such as the language name in
your native language).

This will generate a `messages.po`, a `data_str.po`, and a `story.po` in
`singularity/i18n/lang_<ll_CC>` and from there you can use your
favourite po-file editor to start translating.

### Testing a translation

The singularity game will automatically use your translations once you
have saved them in the relevant po-files.  To verify or review the
translations, please:

 * Start the game from the git checkout (see the README for
   instructions)
     * Note that you will need to start the game in cheat mode to verify
       the cheat translations (cheat mode cannot be enabled later).
 * Navigate to Options, select your language and click OK.  (First
   time only or if you are reviewing multiple translations)
 * Start playing/navigating around to verify that the translations are
   as expected.

### Submitting a new translation or a translation update

Please submit it as a pull request against the master branch via
https://github.com/singularity/singularity/pulls.
