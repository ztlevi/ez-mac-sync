# EZ-MAC-SYNC ☁️

This is a simple script helps people sync their applications across all their mac devices easily.

## Prerequisites

1. [Homebrew](https://brew.sh/)
2. [mas](https://github.com/mas-cli/mas)
3. A cloud service, e.g. Dropbox, Google Drive, iCloud

Scripts to install prerequisites

```shell
# Homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Mas
brew install mas
```

## Usage

1. Download the source code, then `cd` into `ez-mac-sync`.
2. `$ chmod +x ./ezmacsync.py`
3. `./ezmacsync.py`
4. You can alias this script in your shell setting, e.g. `alias update-mac=~/ez-mac-synd/ezmacsync.py`.

For the fist time, you need to input your cloud directory (relative to your HOME path). For example, `Dropbox/AppList`, and the syncing file will be saved under `$HOME/Dropbox/AppList`.

A `.ezmacsyncrc` file will be created under your HOME directory. You can put applications you want to remove across all your mac devices in this file.

```json
{
  "cloudDir": "Dropbox/AppList",
  "brewRemoveList": [],
  "masRemoveList": ["Final Cut Pro", "Compressor", "Motion", "Logic Pro X", "MainStage 3"],
  "brewCaskRemoveList": ["eclipse-jee", "android-studio", "gitkraken"]
}
```

> **Note**: `mas` applications will not be removed from your mac because `mas` cannot uninstall apps, but it will notify you the apps you might need to manually uninstall.

## Upgrading Apps

For upgrading brew apps, use `bubu`

```shell
alias bubo=brew update && brew outdated
alias bubc=brew upgrade && brew cleanup
alias bubu=bubo && bubc
```

For upgrading brew cask apps, see [homebrew-cask-upgrade](https://github.com/buo/homebrew-cask-upgrade).

```shell
brew tap buo/cask-upgrade
brew cu
```
