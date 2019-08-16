#!/usr/local/bin/python3
__author__ = "Ting Zhou"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "ztlevi1993@gmail.com"

import json
import os
import subprocess

if __name__ == "__main__":
    HOME = os.path.expanduser("~")
    CLOUD_DIR = HOME + "/" + "Dotfiles/ezmacsync"

    if not os.path.isdir(CLOUD_DIR):
        os.makedirs(CLOUD_DIR)

    # #################################################################################################
    # get ignore_lists configs
    # #################################################################################################

    ignore_lists_file = CLOUD_DIR + "/ignore_lists.json"
    ignore_lists = {}
    if not os.path.exists(ignore_lists_file):
        open(ignore_lists_file, "w+")
        print("ignore_lists.json file created...")
    else:
        with open(ignore_lists_file) as f:
            ignore_lists = json.load(f)
            print("ignore_lists.json file loaded...")

    ignore_keys = [
        "brewTapRemoveList",
        "brewRemoveList",
        "brewCaskRemoveList",
        "masRemoveList",
    ]
    for key in ignore_keys:
        if key not in ignore_lists:
            ignore_lists[key] = []

    for k, v in ignore_lists.items():
        ignore_lists[k] = sorted(v)

    # dump ignore_lists
    with open(ignore_lists_file, "w+") as f:
        json.dump(ignore_lists, f, indent=2, separators=(",", ":"))

    # #################################################################################################
    # get synced_lists data
    # #################################################################################################
    synced_lists_file = CLOUD_DIR + "/synced_lists.json"
    synced_lists = {}
    if not os.path.exists(synced_lists_file):
        open(synced_lists_file, "w+")
        print("synced_lists.json file created...")
    else:
        with open(synced_lists_file) as f:
            synced_lists = json.load(f)
            print("synced_lists.json file loaded...")

    # make sure every key exists in synced_lists
    synced_keys = [
        "allAppList",
        "brewTapList",
        "brewAppList",
        "brewCaskAppList",
        "masAppList",
    ]
    for key in synced_keys:
        if key not in synced_lists:
            synced_lists[key] = []

    print("================ Backup Start ================")
    # #################################################################################################
    # backup /Applications
    # #################################################################################################
    print("Backup /Applications...")
    all_apps = list(
        filter(lambda app: not app.startswith("."), os.listdir("/Applications"))
    )
    all_apps = list(set(all_apps) | set(synced_lists["allAppList"]))
    synced_lists["allAppList"] = all_apps

    # #################################################################################################
    # update homebrew
    # #################################################################################################
    os.system("/usr/local/bin/brew update")

    # #################################################################################################
    # backup brew tap
    # #################################################################################################
    print("Backup brew taps...")
    brew_taps = (
        subprocess.check_output("/usr/local/bin/brew tap", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    brew_taps = list(set(brew_taps) | set(synced_lists["brewTapList"]))
    brew_taps_ignore_set = set(
        map(lambda tap: tap.lower(), ignore_lists["brewTapRemoveList"])
    )
    brew_taps = list(
        filter(lambda app: app.lower() not in brew_taps_ignore_set, brew_taps)
    )
    try:
        brew_taps.remove("")
    except ValueError:
        pass
    synced_lists["brewTapList"] = brew_taps

    # #################################################################################################
    # backup brew apps
    # #################################################################################################
    print("Backup brew apps...")
    brew_apps = (
        subprocess.check_output("/usr/local/bin/brew list", shell=True)
        .decode("utf-8")
        .split("\n")
    )
    brew_apps = list(set(brew_apps) | set(synced_lists["brewAppList"]))
    brew_ignore_set = set(map(lambda app: app.lower(), ignore_lists["brewRemoveList"]))
    brew_apps = list(filter(lambda app: app.lower() not in brew_ignore_set, brew_apps))
    try:
        brew_apps.remove("")
    except ValueError:
        pass
    synced_lists["brewAppList"] = brew_apps

    # #################################################################################################
    # backup brew cask apps
    # #################################################################################################
    print("Backup brew cask apps...")
    brew_cask_apps = (
        subprocess.check_output("/usr/local/bin/brew cask list", shell=True)
        .decode("utf-8")
        .split("\n")
    )
    brew_cask_apps = list(set(brew_cask_apps) | set(synced_lists["brewCaskAppList"]))
    brew_cask_ignore_set = set(
        map(lambda app: app.lower(), ignore_lists["brewCaskRemoveList"])
    )
    brew_cask_apps = list(
        filter(lambda app: app.lower() not in brew_cask_ignore_set, brew_cask_apps)
    )
    try:
        brew_cask_apps.remove("")
    except ValueError:
        pass
    synced_lists["brewCaskAppList"] = brew_cask_apps

    # #################################################################################################
    # backup mas apps
    # #################################################################################################
    print("Backup mas apps...")
    mas_apps = (
        subprocess.check_output("/usr/local/bin/mas list", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    def split_mas_app(app):
        i1 = app.find(" ")
        i2 = app.find("(")
        return (app[:i1], app[i1 + 1 : i2 - 1])

    mas_apps = map(split_mas_app, mas_apps)
    mas_apps_local = list(mas_apps)
    mas_apps = list(
        set(mas_apps) | set(map(lambda i: tuple(i), synced_lists["masAppList"]))
    )
    mas_ignore_set = set(map(lambda app: app.lower(), ignore_lists["masRemoveList"]))
    mas_apps = list(filter(lambda app: app[1].lower() not in mas_ignore_set, mas_apps))
    try:
        mas_apps.remove(("", ""))
    except ValueError:
        pass
    synced_lists["masAppList"] = mas_apps

    # Sort list
    for k, v in synced_lists.items():
        synced_lists[k] = sorted(v)

    with open(synced_lists_file, "w+") as f:
        json.dump(synced_lists, f, indent=2, separators=(",", ":"))

    # try prettier json files
    try:
        print("Format eamacsync files...")
        os.system(HOME + "/.npm-global/bin/prettier --write " + ignore_lists_file)
        os.system(HOME + "/.npm-global/bin/prettier --write " + synced_lists_file)
        print("\n")
    except:
        print("No prettier installed, pass the formatting...")

    print("================ Backup End ================")

    # #################################################################################################
    # Start Installation
    # #################################################################################################
    print("================ Install Start =================")
    install_script = ""
    # brew tap install
    for tap in synced_lists["brewTapList"]:
        install_script += "brew tap " + tap + "\n"
    if ignore_lists["brewTapRemoveList"]:
        for tap in ignore_lists["brewTapRemoveList"]:
            install_script += "brew untap " + tap + "\n"

    # brew apps install script
    for app in synced_lists["brewAppList"]:
        install_script += "brew install " + app + "\n"
    if ignore_lists["brewRemoveList"]:
        install_script += (
            "brew uninstall " + " ".join(ignore_lists["brewRemoveList"]) + " --force\n"
        )

    # brew cask apps install script
    for cask in synced_lists["brewCaskAppList"]:
        install_script += "brew cask install " + cask + "\n"
    if ignore_lists["brewCaskRemoveList"]:
        install_script += (
            "brew cask uninstall "
            + " ".join(ignore_lists["brewCaskRemoveList"])
            + " --force\n"
        )

    # mas apps install script
    for app in synced_lists["masAppList"]:
        install_script += "mas install " + app[0] + "\n"

    # exec the install script
    print(install_script)
    os.system(install_script)

    mas_apps_need_removal = list(
        filter(lambda app: app[1].lower() in mas_ignore_set, mas_apps_local)
    )
    mas_apps_need_removal = map(lambda app: app[1], mas_apps_need_removal)
    if mas_apps_need_removal:
        print(
            "\nYou might need to remove {} manually.".format(
                ",".join(mas_apps_need_removal)
            )
        )

    print("\n================ Install End =================")
