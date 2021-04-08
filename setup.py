#!/usr/bin/env python3

from distutils.errors import DistutilsSetupError
from distutils import log
import ctypes.util
import os
import re
import subprocess
import shutil
import sys

from setuptools import Distribution, setup
from setuptools.command.install import install


class BinaryDistribution(Distribution):

    def has_ext_modules(self):
        return True


class Install(install):

    def run(self):
        if sys.platform.startswith('linux'):
            # On Linux, ctypes.util.find_library does not return a absolute path...
            listing = subprocess.check_output('ldconfig -p'.split(), stdin=subprocess.DEVNULL)
            for line in listing.decode().split('\n'):
                # libusb-1.0.so (libc6,x86-64) => /usr/lib/libusb-1.0.so
                m = re.match(r'^\s+(?P<basename>libusb-1\.0\.so(?P<version>\.\d+)?) \(libc6,x86-64\)\s+=>\s+(?P<abspath>[^ ]+(?P=basename))$', line)
                if m is not None:
                    libusb_path = m.group('abspath')
                    libusb_name = os.path.basename(libusb_path)
                    version = m.group('version')
                    if version is not None:
                        libusb_name = libusb_name[:-len(version)]
                    break
            else:
                libusb_path, libusb_name = None
        elif sys.platform.startswith('darwin'):
            libusb_path = ctypes.util.find_library('usb-1.0')
            libusb_name = os.path.basename(libusb_path)
        elif sys.platform.startswith('win32'):
            libusb_path = ctypes.util.find_library('libusb-1.0')
            libusb_name = os.path.basename(libusb_path)
        else:
            raise DistutilsSetupError('unsupported platform: %s' % sys.platform)
        assert None not in (libusb_path, libusb_name)
        # Force platlib installation (otherwise purelib).
        self.install_lib = self.install_platlib
        super().run()
        libusb_install = os.path.join(self.install_lib, 'pyusb_libusb1_backend', libusb_name)
        log.info('copying %s => %s' % (libusb_path, libusb_install))
        shutil.copy(libusb_path, libusb_install)


setup(cmdclass={'install': Install}, distclass=BinaryDistribution)
