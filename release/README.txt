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

Steps for cutting a new release:

Before cutting the tag:
   * Update the version number in singularity/__init__.py.
   * Update the version number in singularity/code/savegame.py if needed
   * Update the version number at the top of README.md.
   * Update the release date at the top of the Changelog.
   * Check TODO and remove any entries that are now done in the new
     version.
   * Clean up the master instance of singularity by running 'git status'
     and removing any suspicious files (error logs, swap files, etc.)

To cut the tag:
   * $ cd singularity               # The root, where this file is.
   * $ git pull                     # Make sure that everything is up-to-date.
   * $ git commit                   # Actually make the release.
   * $ git tag vx.yy                # Generate the release.


After cutting the tag:
   * Generate the tarball:
      * $ git archive --worktree-attributes --prefix=singularity-x.y/ -o singularity-x.y.tar.gz vx.y
   * Generate the py2exe:
      * Extract tarball (if Windows machine lacks ability)
      * Copy directory to windows computer with python, pygame, numpy, polib and py2exe.
      * Run c:\Python3\Python.exe setup.py py2exe -b 1
      * Copy the 4 files in dist to root dir.
      * Delete dist and build directories. Test.
      * Go up one level and choose Send to->Zip. Rename properly (singularity-x.yy-win.zip)
   * Upload to site.
   * Update index.html, and singularity/index.html
   * Check to see if screenshot is out-of-date, and update if needed.
   * Also, pypi.python.org.
   * Announce on [endgame-singularity] and [endgame-singularity-dev].

Post-release cleanup:
   * Add a new section at the top of Changelog.
   * Update the version number in singularity/__init__.py to next-release_pre.
   * Update the version number in setup.py to the same.
   * Update the version number at the top of README.md to the same.
   * Add a new milestone to the Github issue tracker, if necessary.
