# Copyright (C) 2005  Adam Bark apb_4@users.sourceforge.net

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""The start of a substitute Clock for pygame"""

import time

class Clock:
    """This class is generally used to limit the framerate of a game.

    Clock().tick(50) called in every frame will limit the framerate to 50
    frames per second. The tick method returns an int corresponding to the
    time since the last call to tick in milliseconds.
    """
    def __init__(self):
        self.t = time.time()

    def tick(self, rate=-1):
        # rate=-1 will be caught by the except statement if no rate is specified
        """If rate is specified this will limit the framerate to the
        specified number per second.
        """
        self.rate = rate
        self._stop()
        retVal = int(round((time.time() - self.t) * 1000, 0))
        self.t = time.time()
        return retVal

    def _stop(self):
        try:

            # There are problems if you try to sleep for a negative amount of
            # time.  Windows interprets it as a really long time.  Strangeness
            # ensues.  So we sleep iff sleep_time > 0 instead of relying on
            # the math to be right.
            sleep_time = 1.0/self.rate - (time.time() - self.t)
            if sleep_time > 0:
               time.sleep(sleep_time)
        except IOError:
            # This will catch exceptions raised if the actual framerate is less
            # than self.rate or if no rate was passed to tick.
            pass

if __name__ == "__main__":
    import timeit
    timer = timeit.Timer('c.tick(50)', 'from __main__ import Clock; c = Clock()')
    print timer.timeit(5000)
