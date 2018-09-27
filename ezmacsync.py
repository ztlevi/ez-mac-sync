#!/usr/bin/python
__author__ = "Ting Zhou"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "ztlevi1993@gmail.com"

import json
import os
import subprocess


if __name__ == "__main__":
    home = os.path.expanduser("~")

    # region get ignore_lists configs
    ignore_lists_file = home + '/.ezmacsyncrc'
    ignore_lists = {}
    if not os.path.exists(ignore_lists_file):
        open(ignore_lists_file, 'w+')
        print("ignore_lists.json file created...")
    else:
        with open(ignore_lists_file) as f:
            ignore_lists = json.load(f)
            print("ignore_lists.json file loaded...")

    # make sure every key exists in ignore list config file
    if 'cloudDir' not in ignore_lists or not ignore_lists['cloudDir']:
        cloud_path = raw_input(
            'Input your cloud directory relative to $HOME for syncing...\ne.g. Dropbox/AppList\n')
        ignore_lists['cloudDir'] = cloud_path
    cloud_dir = home + '/' + ignore_lists['cloudDir']
    if not os.path.isdir(cloud_dir):
        os.makedirs(cloud_dir)

    ignore_keys = ['brewTapRemoveList', 'brewRemoveList',
                   'brewCaskRemoveList', 'masRemoveList']
    for key in ignore_keys:
        if key not in ignore_lists:
            ignore_lists[key] = []

    # dump ignore_lists
    with open(ignore_lists_file, 'w+') as f:
        json.dump(ignore_lists, f, indent=2, separators=(',', ':'))
    # endregion

    # region get synced_lists data
    synced_lists_file = cloud_dir + "/synced_lists.json"
    synced_lists = {}
    if not os.path.exists(synced_lists_file):
        open(synced_lists_file, 'w+')
        print('synced_lists.json file created...')
    else:
        with open(synced_lists_file) as f:
            synced_lists = json.load(f)
            print('synced_lists.json file loaded...')

    # make sure every key exists in synced_lists
    synced_keys = ["allAppList", "brewTapList", "brewAppList",
                   "brewCaskAppList", "masAppList"]
    for key in synced_keys:
        if key not in synced_lists:
            synced_lists[key] = []

    # dump synced_lists
    with open(synced_lists_file, 'w+') as f:
        json.dump(synced_lists, f, indent=2, separators=(',', ':'))

    print('================ Backup Start ================')
    # endregion

    # region backup /Applications
    print('Backup /Applications...')
    all_apps = filter(lambda app: not app.startswith('.'),
                      os.listdir('/Applications'))
    all_apps = list(set(all_apps)
                    | set(synced_lists["allAppList"]))
    synced_lists["allAppList"] = all_apps
    # endregion

    # update brew
    os.system('/usr/local/bin/brew update')

    # region backup brew tap
    print('Backup brew taps...')
    brew_taps = subprocess.check_output(
        '/usr/local/bin/brew tap', shell=True).strip('\n').split('\n')
    brew_taps = list(set(brew_taps) | set(synced_lists['brewTapList']))
    brew_taps_ignore_set = set(
        map(lambda tap: tap.lower(), ignore_lists['brewTapRemoveList']))
    brew_taps = filter(lambda app: app.lower()
                       not in brew_taps_ignore_set, brew_taps)
    synced_lists['brewTapList'] = brew_taps
    # endregion

    # region backup brew apps
    print('Backup brew apps...')
    brew_apps = subprocess.check_output(
        '/usr/local/bin/brew list', shell=True).strip('\n').split('\n')
    brew_apps = list(set(brew_apps) | set(synced_lists['brewAppList']))
    brew_ignore_set = set(
        map(lambda app: app.lower(), ignore_lists['brewRemoveList']))
    brew_apps = filter(lambda app: app.lower()
                       not in brew_ignore_set, brew_apps)
    synced_lists['brewAppList'] = brew_apps
    # endregion

    # region backup brew cask apps
    print('Backup brew cask apps...')
    brew_cask_apps = subprocess.check_output(
        '/usr/local/bin/brew cask list', shell=True).strip('\n').split('\n')
    brew_cask_apps = list(set(brew_cask_apps) | set(
        synced_lists['brewCaskAppList']))
    brew_cask_ignore_set = set(
        map(lambda app: app.lower(), ignore_lists['brewCaskRemoveList']))
    brew_cask_apps = filter(lambda app: app.lower(
    ) not in brew_cask_ignore_set, brew_cask_apps)
    synced_lists['brewCaskAppList'] = brew_cask_apps
    # endregion

    # region backup mas apps
    print('Backup mas apps...')
    mas_apps = subprocess.check_output(
        '/usr/local/bin/mas list', shell=True).strip('\n').split('\n')

    def split_mas_app(app):
        i1 = app.find(' ')
        i2 = app.find('(')
        return (app[:i1], app[i1 + 1:i2 - 1])

    mas_apps = map(split_mas_app, mas_apps)
    mas_apps_local = list(mas_apps)
    mas_apps = list(set(mas_apps) | set(
        map(lambda i: tuple(i), synced_lists['masAppList'])))
    mas_ignore_set = set(
        map(lambda app: app.lower(), ignore_lists['masRemoveList']))
    mas_apps = filter(lambda app: app[1].lower()
                      not in mas_ignore_set, mas_apps)
    synced_lists['masAppList'] = mas_apps

    with open(synced_lists_file, 'w+') as f:
        json.dump(synced_lists, f, indent=2, separators=(',', ':'))
    # endregion

    print('================ Backup End ================')

    print('================ Install Start =================')
    install_script = ''
    # brew apps install script
    install_script += 'brew install ' + \
                      ' '.join(synced_lists['brewAppList']) + '\n'
    if ignore_lists['brewRemoveList']:
        install_script += 'brew uninstall ' + \
                          ' '.join(
                              ignore_lists['brewRemoveList']) + ' --force\n'

    # brew cask apps install script
    install_script += 'brew cask install ' + \
                      ' '.join(synced_lists['brewCaskAppList']) + '\n'
    if ignore_lists['brewCaskRemoveList']:
        install_script += 'brew cask uninstall ' + \
                          ' '.join(
                              ignore_lists['brewCaskRemoveList']) + ' --force\n'

    # mas apps install script
    for app in synced_lists['masAppList']:
        install_script += 'mas install ' + app[0] + '\n'

    # exec the install script
    os.system(install_script)

    mas_apps_need_removal = filter(
        lambda app: app[1].lower() in mas_ignore_set, mas_apps_local)
    mas_apps_need_removal = map(lambda app: app[1], mas_apps_need_removal)
    if mas_apps_need_removal:
        print('\nYou might need to remove {} manually.'.format(
            ','.join(mas_apps_need_removal)))

    print('\n================ Install End =================')
