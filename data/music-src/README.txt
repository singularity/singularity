Included here are the source Psycle files for the original music tracks
created for Endgame: Singularity and also the source Renoise files for the
extended music sountrack, both downloadable separately and created by Max
McCracken.

Pre-encoded music in Ogg Vorbis format for both original and extended soundtrack
can be downloaded at Max McCracken's website:

     http://www.soundcloud.com/maxstack

And also at Endgame: Singularity download hosts:

    http://www.emhsoft.com/singularity
    https://github.com/singularity/singularity-music

Be aware that the Ogg Vorbis songs available at Endgame: Singularity hosts were
re-encoded from source to better fit the game (smaller size, ReplayGain normali-
zation etc), and thus are not bitwise identical to the ones at author's website.

Lossless versions of the songs in FLAC format are also available at:

    https://github.com/singularity/singularity-music-lossless-original
    https://github.com/singularity/singularity-music-lossless-extended


To generate your own files from the Psycle (.psy) original sountrack sources:

* Download Psycle from:

     http://psycle.pastnotecut.org/

  Note that Psycle is Windows-only, but it runs fine in current-enough
  releases of WINE.

* Download the Drumatic VE VST from:

     http://www.e-phonic.com/plugins/drumatic_ve.php

  and install it into Psycle's directories.  The included INSTALLATION.TXT
  explains the process, but the .dll goes into VstPlugins and the subdirectory
  goes directly into Psycle's directory.

* Load Psycle up.

* Go to View->Add Machine and click the 'Rescan all plugins...' button.  This
  will make Psycle detect the Drumatic VE VST plugin.

* Load one of the .psy files via File->Open and choose File->Render as WAV.
  You'll need to pick a sample rate here.  The canonical sample rate is 48000 Hz


To generate your own files from the Renoise (.xrns) extended sountrack sources:

* Download Renoise from:

     http://www.renoise.com

  Renoise is available for Windows, Mac OSX and Linux. A greate Linux release
  info, including a mini tutorial for Renoise itself, can be found at:

     http://www.linuxjournal.com/content/renoise-linux

* Run Renoise, open the .xrns files and export them to Vorbis format (.ogg).
  Or you may convert them to MIDI format using the MidiConvert plugin found at:

    http://www.renoise.com/tools/midi-convert

* It's also possible to convert the songs to MIDI without installing Renoise,
  using the (deprecated) xrns2midi standalone PHP script found at:

    http://xrns-php.sourceforge.net/xrns2midi.html

* Some commercial instruments were used by the author to create the songs, and
  are required to make the generated files sound the same as the pre-encoded
  ones available for download.
