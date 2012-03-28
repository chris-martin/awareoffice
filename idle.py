# https://gist.github.com/1879754

# We run this script as a separate process because, for reasons unknown,
# it gives a segmentation fault when run by a sub-thread.

import ctypes, os

class XScreenSaverInfo( ctypes.Structure):
  """ typedef struct { ... } XScreenSaverInfo; """
  _fields_ = [('window',      ctypes.c_ulong), # screen saver window
              ('state',       ctypes.c_int),   # off,on,disabled
              ('kind',        ctypes.c_int),   # blanked,internal,external
              ('since',       ctypes.c_ulong), # milliseconds
              ('idle',        ctypes.c_ulong), # milliseconds
              ('event_mask',  ctypes.c_ulong)] # events

xlib = ctypes.cdll.LoadLibrary('libX11.so')
display = xlib.XOpenDisplay(os.environ['DISPLAY'])
xss = ctypes.cdll.LoadLibrary('libXss.so.1')
xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
xssinfo = xss.XScreenSaverAllocInfo()
xss.XScreenSaverQueryInfo(display, xlib.XDefaultRootWindow(display), xssinfo)

print "%d" % xssinfo.contents.idle
