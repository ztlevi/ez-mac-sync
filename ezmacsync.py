#!/usr/bin/python
__author__ = "Ting Zhou"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "ztlevi1993@gmail.com"

import json
import os
import subprocess


def create_file_if_not_exist(file, initial_data=None):
    if not os.path.exists(file):
        with open(file, 'w+') as f:
            if initial_data:
                json.dump(initial_data, f, indent=2)


if __name__ == "__main__":
    home = os.path.expanduser("~")

    # get ignore_lists configs
    ignore_lists_file = home + '/.ezmacsyncrc'
    initial_ignore_lists = {"cloudDir": "", "brewRemoveList": [
    ], "brewCaskRemoveList": [], "masRemoveList": []}
    create_file_if_not_exist(ignore_lists_file, initial_ignore_lists)
    with open(ignore_lists_file) as f:
        ignore_lists = json.load(f)
        print("ignore_lists.json file loaded...")
    if 'cloudDir' not in ignore_lists or not ignore_lists['cloudDir']:
        cloud_path = raw_input(
            'Input your cloud directory relative to $HOME for syncing...\ne.g. Dropbox/AppList\n')
        ignore_lists['cloudDir'] = cloud_path
    cloud_path = ignore_lists['cloudDir']
    with open(ignore_lists_file, 'w+') as f:
        json.dump(ignore_lists, f, indent=2)

    cloud_dir = home + '/' + cloud_path
    if not os.path.isdir(cloud_dir):
        os.makedirs(cloud_dir)

    # get synced_lists data
    synced_lists_file = cloud_dir + "/synced_lists.json"
    initial_synced_lists = {"allAppList": [], "brewAppList": [
    ], "brewCaskAppList": [], "masAppList": []}
    create_file_if_not_exist(synced_lists_file, initial_synced_lists)
    with open(synced_lists_file) as f:
        synced_lists = json.load(f)
        print('synced_lists.json file loaded...')

    print('================ Backup Start ================')

    # backup /Applications
    print('Backup /Applications...')
    all_apps = list(set(os.listdir('/Applications'))
                    | set(synced_lists["allAppList"]))
    synced_lists["allAppList"] = all_apps

    # backup brew apps
    print('Backup brew apps...')
    brew_apps = subprocess.check_output(
        '/usr/local/bin/brew list', shell=True).strip('\n').split('\n')
    brew_apps = list(set(brew_apps) | set(synced_lists['brewAppList']))
    brew_ignore_set = set(
        map(lambda app: app.lower(), ignore_lists['brewRemoveList']))
    brew_apps = filter(lambda app: app.lower()
                       not in brew_ignore_set, brew_apps)
    synced_lists['brewAppList'] = brew_apps

    # backup brew cask apps
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

    # backup mas apps
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
        json.dump(synced_lists, f, indent=2)

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
