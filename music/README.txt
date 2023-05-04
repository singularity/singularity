Here is where you can place the official music pack available at:

   https://github.com/singularity/singularity-music

And also at the official website:

   http://emhsoft.com/singularity

While Pygame supports both Ogg Vorbis and MP3, its MP3 support is less
stable.  If you encounter problems with the game, first remove any MP3s
you may have placed here.

If you obtained Endgame: Singularity as a cloned git repository, you
can also get the official music pack by fetching its singularity-music
submodule. From the singularity root directory, run:

    git submodule update --init singularity/music/singularity-music

(or simply `git submodule update --init singularity-music` from this directory)

There's also available a lossless version of the soundtrack in FLAC
format, in case you want to generate the Ogg Vorbis files yourself:

   https://github.com/singularity/singularity-music-lossless-original
   https://github.com/singularity/singularity-music-lossless-extended

Both also available as git submodules. From repository root:

    git submodule update --init singularity/music/singularity-music-lossless-original
    git submodule update --init singularity/music/singularity-music-lossless-extended
