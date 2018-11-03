#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
import getopt
import os
import subprocess
import sys


use_su = False
version = None


def run_system_command(command):
    print(">>{}".format(command))
    os.system(command)


def adb_get_version():
    cmd = ["adb", "shell", "getprop", "ro.build.version.release"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    line = p.stdout.readline()
    line = line.strip()
    print("version={}".format(line))
    if len(line) == 0:
        sys.exit(1)
    arr = line.split(".")
    return int(arr[0])


def adb_get_abi():
    cmd = ["adb", "shell", "getprop", "ro.product.cpu.abi"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    line = p.stdout.readline()
    line = line.strip()
    if line == "armeabi-v7a":
        return "arm"
    elif line == "arm64-v8a":
        return "arm64"
    elif line == "x86":
        return "x86"
    else:
        print("not support abi")
        sys.exit(1)


def adb_shell(cmd):
    if use_su is False:
        run_system_command("adb shell {}".format(cmd))
    else:
        run_system_command("adb shell su -c {}".format(cmd))


def adb_push(src, dst):
    if use_su is False:
        run_system_command("adb push {} {}".format(src, dst))
    else:
        file_name = os.path.basename(dst)
        run_system_command("adb push {} /data/local/tmp/{}".format(src, file_name))
        run_system_command("adb shell su -c rm {}".format(dst))
        run_system_command("adb shell su -c cp /data/local/tmp/{} {}".format(file_name, dst))
        run_system_command("adb shell su -c rm /data/local/tmp/{}".format(file_name))


def adb_install(src, dst, mode, use_context=False):
    adb_push(src, dst)
    adb_shell("chmod {} {}".format(mode, dst))
    if use_context is True:
        if version < 5:
            adb_shell("chcon u:object_r:system_file:s0 {}".format(dst))
        else:
            adb_shell("chcon u:object_r:zygote_exec:s0 {}".format(dst))


def mount_system():
    adb_shell("mount -o rw,remount /system")
    adb_shell("mkdir -p /sdcard/asan/")


def stop_start():
    adb_shell("stop")
    adb_shell("start")


def install_aosp_4():
    mount_system()
    adb_shell("cp -p /system/bin/app_process /system/bin/app_process32")
    adb_install("pre-lollipop/app_process", "/system/bin/app_process", "0777")
    adb_install("libclang_rt.asan-arm-android.so", "/system/lib/libclang_rt.asan-arm-android.so", "0644")

    stop_start()


def uninstall_aosp_4():
    mount_system()
    adb_shell("cp -p /system/bin/app_process /system/bin/app_process.bak")
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process")

    stop_start()


def install_aosp_arm():
    mount_system()
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process32.real")
    adb_install("lollipop/arm/app_process32", "/system/bin/app_process32", "0755", use_context=True)

    adb_install("libclang_rt.asan-arm-android.so", "/system/lib/libclang_rt.asan-arm-android.so", "0644")

    if version >= 8:
        adb_shell("mv /system/etc/ld.config.txt /system/etc/ld.config.txt.saved")

    stop_start()


def uninstall_aosp_arm():
    mount_system()
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process32.bak")
    adb_shell("cp -p /system/bin/app_process32.real /system/bin/app_process32")

    if version >= 8:
        adb_shell("mv /system/etc/ld.config.txt.saved /system/etc/ld.config.txt")

    stop_start()


def install_aosp_x86():
    mount_system()
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process32.real")
    adb_install("lollipop/x86/app_process32", "/system/bin/app_process32", "0755", use_context=True)

    adb_install("libclang_rt.asan-i686-android.so", "/system/lib/libclang_rt.asan-i686-android.so", "0644")

    if version >= 8:
        adb_shell("mv /system/etc/ld.config.txt /system/etc/ld.config.txt.saved")

    stop_start()


def uninstall_aosp_x86():
    mount_system()
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process32.bak")
    adb_shell("cp -p /system/bin/app_process32.real /system/bin/app_process32")

    if version >= 8:
        adb_shell("mv /system/etc/ld.config.txt.saved /system/etc/ld.config.txt")

    stop_start()

def install_aosp_arm64():
    mount_system()
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process32.real")
    adb_install("lollipop/arm64/app_process32", "/system/bin/app_process32", "0755", use_context=True)

    adb_shell("cp -p /system/bin/app_process64 /system/bin/app_process64.real")
    adb_install("lollipop/arm64/app_process64", "/system/bin/app_process64", "0755", use_context=True)

    adb_install("libclang_rt.asan-arm-android.so",
                "/system/lib/libclang_rt.asan-arm-android.so", "0644")

    adb_install("libclang_rt.asan-aarch64-android.so",
                "/system/lib64/libclang_rt.asan-aarch64-android.so", "0644")

    if version >= 8:
        adb_shell("mv /system/etc/ld.config.txt /system/etc/ld.config.txt.saved")

    stop_start()


def uninstall_aosp_arm64():
    mount_system()
    adb_shell("cp -p /system/bin/app_process32 /system/bin/app_process32.bak")
    adb_shell("cp -p /system/bin/app_process32.real /system/bin/app_process32")

    adb_shell("cp -p /system/bin/app_process64 /system/bin/app_process64.bak")
    adb_shell("cp -p /system/bin/app_process64.real /system/bin/app_process64")

    if version >= 8:
        adb_shell("mv /system/etc/ld.config.txt.saved /system/etc/ld.config.txt")

    stop_start()


if __name__ == '__main__':
    revert = False
    opts, args = getopt.getopt(sys.argv[1:], "", ["revert", "use-su"])
    for op, value in opts:
        if op == "--revert":
            revert = True
        if op == "--use-su":
            use_su = True

    version = adb_get_version()
    if version < 5:
        if revert:
            uninstall_aosp_4()
        else:
            install_aosp_4()
    else:
        abi = adb_get_abi()
        print("abi={}".format(abi))
        adb_shell("setenforce 0")
        if abi == "arm":
            if revert:
                uninstall_aosp_arm()
            else:
                install_aosp_arm()
        elif abi == "arm64":
            if revert:
                uninstall_aosp_arm64()
            else:
                install_aosp_arm64()
        elif abi == "x86":
            if revert:
                uninstall_aosp_x86()
            else:
                install_aosp_x86()
