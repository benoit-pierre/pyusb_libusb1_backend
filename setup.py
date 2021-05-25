#!/usr/bin/env python3

from distutils import log
import os
import subprocess
import sys

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


libusb_dir = 'libusb'
libusb_src_dir = os.path.join(libusb_dir, 'libusb')

libusb_deps = []
libusb_incs = ['{src}']
libusb_srcs = ('''
               {src}/core.c
               {src}/descriptor.c
               {src}/hotplug.c
               {src}/io.c
               {src}/strerror.c
               {src}/sync.c
               '''.split())
libusb_libs = []
libusb_ldflags = []

if sys.platform.startswith('darwin'):
    libusb_deps.extend('''
                       {src}/os/events_posix.h
                       {src}/os/threads_posix.h
                       {src}/os/darwin_usb.h
                       {top}/Xcode/config.h
                       '''.split())
    libusb_incs.insert(0, '{top}/Xcode')
    libusb_srcs.extend('''
                       {src}/os/events_posix.c
                       {src}/os/threads_posix.c
                       {src}/os/darwin_usb.c
                       '''.split())
    libusb_libs.extend('''
                       objc
                       '''.split())
    libusb_ldflags.extend('''
                          -Wl,-framework,IOKit
                          -Wl,-framework,CoreFoundation
                          '''.split())

if sys.platform.startswith('linux'):
    libusb_deps.extend('''
                       {src}/os/events_posix.h
                       {src}/os/threads_posix.h
                       {src}/os/linux_usbfs.h
                       {top}/config.h
                       '''.split())
    libusb_incs.insert(0, '{top}')
    libusb_srcs.extend('''
                       {src}/os/events_posix.c
                       {src}/os/threads_posix.c
                       {src}/os/linux_udev.c
                       {src}/os/linux_usbfs.c
                       '''.split())
    libusb_libs.extend('''
                       udev
                       pthread
                       '''.split())

if sys.platform.startswith('win32'):
    libusb_deps.extend('''
                       {src}/os/events_windows.h
                       {src}/os/threads_windows.h
                       {src}/os/windows_common.h
                       {src}/os/windows_usbdk.h
                       {src}/os/windows_winusb.h
                       {top}/msvc/config.h
                       '''.split())
    libusb_incs.insert(0, '{top}/msvc')
    libusb_srcs.extend('''
                       {src}/os/events_windows.c
                       {src}/os/threads_windows.c
                       {src}/os/windows_common.c
                       {src}/os/windows_usbdk.c
                       {src}/os/windows_winusb.c
                       {src}/libusb-1.0.rc
                       libusb_py_stub.c
                       '''.split())
    libusb_srcs.append('libusb_py_stub.c')
    libusb_ldflags.append('/DEF:{src}/libusb-1.0.def')

for var in libusb_deps, libusb_incs, libusb_srcs, libusb_ldflags:
    for n, v in enumerate(var):
        var[n] = v.format(
            top=libusb_dir,
            src=libusb_src_dir
        )


libusb_extension = Extension(
    'pyusb_libusb1_backend.libusb',
    depends=libusb_deps,
    include_dirs=libusb_incs,
    sources=libusb_srcs,
    libraries=libusb_libs,
    extra_link_args=libusb_ldflags,
    # Make the extension optional, so the package
    # can be installed from source distribution,
    # except when cibuildwheel is being used.
    optional=os.environ.get('CIBUILDWHEEL', '0') != '1',
)


class BuildExt(build_ext):

    def build_extension(self, ext):
        if ext is libusb_extension and \
           os.path.exists(libusb_src_dir) and \
           sys.platform.startswith('linux'):
            # Need to generate `config.h` for the Linux build.
            if not os.path.exists(os.path.join(libusb_dir, 'configure')):
                log.info('running libusb bootstrap.sh')
                subprocess.check_call(('./bootstrap.sh'), cwd=libusb_dir)
            if not os.path.exists(os.path.join(libusb_dir, 'config.h')):
                log.info('running libusb configure')
                subprocess.check_call(('./configure'), cwd=libusb_dir)
        return build_ext.build_extension(self, ext)


setup(cmdclass={'build_ext': BuildExt}, ext_modules=[libusb_extension])
