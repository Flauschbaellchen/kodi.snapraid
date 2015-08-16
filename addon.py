import urlparse
import xbmcgui
import time
import xbmc
import re
import sys
import fcntl, os
from subprocess import PIPE, Popen

class SnapRaid:
    percent_pattern = re.compile('^(?P<percent>\d+)%')
    executable_path = "/usr/bin/snapraid"

    def __init__(self):
        self.percent = 0
        self.lastline = ""

    def synchronize(self):
        self._setupProcessbar("Syncronize")
        self._subcall('sync')

    def scrub(self):
        self._setupProcessbar("Scrub")
        self._subcall('scrub')

    def _setupProcessbar(self, title=""):
        self.progressBar = xbmcgui.DialogProgressBG()
        self.progressBar.create("Snapraid - "+title, "Starting up...")

    def _processLine(self):
        line = None
        try:
            line = self.subprocess.stdout.readline()
        except IOError:
            time.sleep(.1)

        if line is not None:
            self.lastline = line
            matched = self.percent_pattern.match(line)
            if matched:
                self.percent = int(matched.group("percent"))

            self.progressBar.update(self.percent, message=self.lastline)

    def _subcall(self, command):
        self.subprocess = None
        try:
            self.subprocess = Popen([self.executable_path+" "+command], stdout=PIPE)
            fcntl.fcntl(self.subprocess.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        except OSError:
            xbmcgui.Dialog().notification("Error","Could not call Snapraid - is it installed?", time=4000)
            return

        while True:
            self._processLine()
            if self.subprocess.poll() != None:
                break

        self.progressBar.close()


def get_params():
    param = {}

    if(len(sys.argv) > 1):
        for i in sys.argv:
            args = i
            if(args.startswith('?')):
                args = args[1:]
            param.update(dict(urlparse.parse_qsl(args)))

    return param

mode = xbmcgui.Dialog().select(
    "SnapRaid", #title
    ["Synchronize", "Scrub"] ) # possible selections

if (mode != -1):
    if (mode == 0):
        snapraid = SnapRaid()
        snapraid.synchronize()
    elif (mode == 1):
        snapraid = SnapRaid()
        snapraid.scrub()
