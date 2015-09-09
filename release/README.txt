This is the build directory for binary releases, such as Windows and Mac OSX.

Each subdirectory is a git submodule where each commit is a release, tagged so,
ready to be zipped. The zipfile for each release can be automatically generated
and downloaded from github. For example, for the Windows release v0.30c the URL:

    https://github.com/singularity/singularity-windows/archive/v0.30c.zip

Will trigger the download of a file named `singularity-windows-0.30c.zip`.

If you are a developer and want to create and publish a new release, first
fetch and update its submodules. From the singularity root directory, run:

git submodule update --init release/windows

---

As there were no releases since the switch from SVN to git and from Google Code
to Github, there are no official procedures for generating a new release.

The following are the old procedures used to create a new release version, its
windows binaries, and the release tarball, and used to be named `release-steps`
in the old SVN repository.

These steps should NOT be used anymore, they are here for historical purposes,
to be used as a reference for creating the new release steps.

Steps for cutting a new release: [OUTDATED, FOR REFERENCE ONLY! READ ABOVE!]

Before cutting the tag:
   * Update the version number in setup.py.
   * Update the version number in code/g.py.
   * Update the version number at the top of README.txt.
   * Update the release date at the top of the Changelog.
   * Check TODO and remove any entries that are now done in the new
     version.
   * Clean up the trunk instance of singularity by running 'svn status'
     and removing any suspicious files (error logs, swap files, etc.)

To cut the tag:
   * $ cd singularity               # The root, where this file is.
   * $ svn up                       # Make sure that everything is up-to-date.
   * $ svn copy trunk/ tags/singularity-x.yy  # Generate the release.
   * $ svn commit                   # Actually make the release.

After cutting the tag:
   * Generate the tarball:
      * $ cd tags/
      * $ tar --exclude .svn --exclude music --exclude .pyc -cvzf singularity-x.yy-src.tar.gz singularity-x.yy/
   * Generate the py2exe:
      * Extract tarball (if Windows machine lacks ability)
      * Copy directory to windows computer with python, pygame, numpy and py2exe.
      * Run c:\Python24\Python.exe setup.py py2exe -b 1
      * Copy the 4 files in dist to root dir.
      * Delete dist and build directories. Test.
      * Go up one level and choose Send to->Zip. Rename properly (singularity-x.yy-win.zip)
   * Upload to site.
   * Update index.html, and singularity/index.html
   * Check to see if screenshot is out-of-date, and update if needed.
   * Send update notice to happypenguin.org, freshmeat.net and pygame.org.
   * Also, pypi.python.org.
   * Announce on [endgame-singularity] and [endgame-singularity-dev].

Post-release cleanup:
   * Update release-revisions with the revision number of the copy.
     You can get this either from the actual commit (easiest), or
     by running
        $ svn log tags/singularity-x.yy | less
     and looking at the revision number of the top entry.
   * Add a new section at the top of Changelog.
   * Update the version number in code/singularity.py to next-release_pre.
   * Update the version number in setup.py to the same.
   * Update the version number at the top of README.txt to the same.
   * Add a new milestone to the Google Code issue tracker, if necessary.
