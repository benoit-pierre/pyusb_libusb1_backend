#!/usr/bin/env python3

from importlib.util import find_spec
import ctypes

spec = find_spec('pyusb_libusb1_backend.libusb')
assert spec is not None
libusb = ctypes.CDLL(spec.origin)
