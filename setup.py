#!/usr/bin/env python3

import os
import subprocess
import sys

from setuptools import Extension, setup


libusb_dir = 'libusb'
libusb_src_dir = os.path.join(libusb_dir, 'libusb')

libusb_incs = [libusb_src_dir]
libusb_srcs = ('''
               core.c
               descriptor.c
               hotplug.c
               io.c
               strerror.c
               sync.c
               '''.split())
libusb_libs = []
libusb_ldflags = []

if sys.platform.startswith('darwin'):
    libusb_incs.insert(0, os.path.join(libusb_dir, 'Xcode'))
    libusb_srcs.extend('''
                       os/events_posix.c
                       os/threads_posix.c
                       os/darwin_usb.c
                       '''.split())
    libusb_libs.extend('''
                       objc
                       '''.split())
    libusb_ldflags.extend('''
                          -Wl,-framework,IOKit
                          -Wl,-framework,CoreFoundation
                          '''.split())

if sys.platform.startswith('linux'):
    if not os.path.exists(os.path.join(libusb_dir, 'configure')):
        subprocess.check_call(('./bootstrap.sh'), cwd=libusb_dir)
    if not os.path.exists(os.path.join(libusb_dir, 'config.h')):
        subprocess.check_call(('./configure'), cwd=libusb_dir)
    libusb_incs.append(libusb_dir)
    libusb_srcs.extend('''
                       os/events_posix.c
                       os/threads_posix.c
                       os/linux_usbfs.c
                       os/linux_udev.c
                       '''.split())
    libusb_libs.extend('''
                       udev
                       pthread
                       '''.split())

libusb_srcs = [
    os.path.join(libusb_src_dir, src)
    for src in libusb_srcs
]

libusb_extension = Extension(
    'pyusb_libusb1_backend.libusb',
    include_dirs=libusb_incs,
    sources=libusb_srcs,
    libraries=libusb_libs,
    extra_link_args=libusb_ldflags,
)

setup(ext_modules=[libusb_extension])
