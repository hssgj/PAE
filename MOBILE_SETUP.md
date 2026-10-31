# PAE Mobile — canonical main

Mobile sources now live in main with the CLI. The older pae-mobile-mvp branch is a historical source, not a separate current installation target.

## Existing phone installation

First preserve local changes and collect its source inventory. Do not blindly pull, reset, switch branches or rerun historical installers. Follow [START_HERE](docs/START_HERE.md). This repository update has not changed the phone itself.

## Clean checkout only

Clone hssgj/PAE main into an unused directory. Provision the existing llama-server and model as required by start-mobile.sh; model weights and credentials are not in Git.

Run `bash start-mobile.sh`. The local browser endpoint is http://127.0.0.1:8765. The launcher can use PAE_ROOT for an alternate checkout. This is local HTTP inside the phone.

The Android shell source is in pae-android. Its existing build workflow is retained. APK build/install and Run commands in Termux environment permission still require actual Android verification. Enabling external Termux commands should be a deliberate device configuration step.

Current cloud launchers start CLI sessions; the existing mobile launcher still selects the local backend. There is no automatic model turntable.
