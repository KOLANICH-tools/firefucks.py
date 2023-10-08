firefucks.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
============
~~[wheel (GitLab)](https://gitlab.com/KOLANICH-tools/firefucks.py/-/jobs/artifacts/master/raw/dist/firefucks-0.CI-py3-none-any.whl?job=build)~~
[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-tools/firefucks.py/workflows/CI/master/firefucks-0.CI-py3-none-any.whl)
~~![GitLab Build Status](https://gitlab.com/KOLANICH-tools/firefucks.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH-tools/firefucks.py/badges/master/coverage.svg)~~
[![GitHub Actions](https://github.com/KOLANICH-tools/firefucks.py/workflows/CI/badge.svg)](https://github.com/KOLANICH-tools/firefucks.py/actions/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-tools/firefucks.py.svg)](https://libraries.io/github/KOLANICH-tools/firefucks.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

**We have moved to https://codeberg.org/KOLANICH-tools/firefucks.py, grab new versions there.**

Under the disguise of "better security" Micro$oft-owned GitHub has [discriminated users of 1FA passwords](https://github.blog/2023-03-09-raising-the-bar-for-software-security-github-2fa-begins-march-13/) while having commercial interest in success of [FIDO 1FA specifications](https://fidoalliance.org/specifications/download/) and [Windows Hello implementation](https://support.microsoft.com/en-us/windows/passkeys-in-windows-301c8944-5ea2-452b-9886-97e4d2ef4422) which [it promotes as a replacement for passwords](https://github.blog/2023-07-12-introducing-passwordless-authentication-on-github-com/). It will result in dire consequencies and is competely inacceptable, [read why](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

If you don't want to participate in harming yourself, it is recommended to follow the lead and migrate somewhere away of GitHub and Micro$oft. Here is [the list of alternatives and rationales to do it](https://github.com/orgs/community/discussions/49869). If they delete the discussion, there are certain well-known places where you can get a copy of it. [Read why you should also leave GitHub](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).


This is a tool for patching Firefox Web Browser into allowing unsigned addons.

Can be used as an apt hook.

Mozilla, requiring extensions signing and signing in and getting 2FA for AMO is not nice. 🖕🔥

This tool has been created as a response to
* will of Mozilla to disallow unsigned extensions in regular builds of Firefox;
* will of Mozilla to disallow WebExtensions Experiments in regular builds of Firefox;
* will of Mozilla to require authentication on AMO in order to sign extensions;
* unwillingness of devs of some distros to provide "Developer Edition" builds of Firefox.

ToDo: Currently libzip is used for updating files witin the archive. It doesn't allow rewriting files in archives without creating a copy of the archive. [It is considered contradicting `libzip` goals according to its authors.](https://github.com/nih-at/libzip/issues/304) We need a lib allowing to do that.

## Installation
0. Learn how to install python packages from git.
1. Install manually the latest versions of the dependencies mentioned in the `Dependencies` section of this ReadMe.
2. Install this tool.

## How to use
1. Copy the original `omni.ja` to the current dir
```bash
cp /usr/lib/firefox/omni.ja ./omni.ja.bak
cp ./omni.ja.bak ./omni.ja
```
2. Modify it with `firefucks` tool
```bash
firefucks ./omni.ja
```
3. Copy it back
```bash
sudo fakeroot cp ./omni.ja /usr/lib/firefox/omni.ja
```
4. **IMPORTANT, without this the changes will have no effect!** (ToDo: figure out what is the internal mechanism invalidating the caches, and maybe the way to patch the data within caches without needing root). Clean the startup caches:
```bash
rm -rf ~/.cache/mozilla/firefox/*/startupCache
```

## Check that it has worked
1. Open `Tools -> Browser Tools -> Browser Console`.
2. Paste there content of [`snippet.js`](./snippet.js) and execute it. It will print an object with the current values of the variables.
3. Compare them against the [`preset.json` file](./firefucks/preset.json) shipped as a part of this tool.


## Principle of operation

Some critical browser-related code written in JS and some resources are stored in `omni.ja` files, which are zip archives. The location of these files is following:

```bash
dpkg -L firefox | grep omni.ja
```

```
/usr/lib/firefox/browser/omni.ja
/usr/lib/firefox/omni.ja
```

The latter of them (`/usr/lib/firefox/omni.ja`) contains:
* Module `modules/AppConstants.jsm`, which contains some constants used to distinguish between flavours of Firefox;
* Module `modules/addons/AddonSettings.jsm`, which contains some code, using the constants from `AppConstants` as input. Module `modules/addons/AddonConstants.jsm` [no longer exists](https://hg.mozilla.org/mozilla-central/rev/2766cd8808dd2d1d66bc4e9e9e313bbc60b9a197) because of this one.
* `jsloader/resource/gre` is no longer present.


Some of them are documented by the links:
* https://firefox-source-docs.mozilla.org/toolkit/components/telemetry/internals/preferences.html
* https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html
* https://wiki.mozilla.org/Platform/Channel-specific_build_defines

We are particulary interested in the following properties:
* [`MOZ_REQUIRE_SIGNING`](https://searchfox.org/mozilla-central/search?q=symbol:AppConstants%23MOZ_REQUIRE_SIGNING), which is used to override the value `xpinstall.signatures.required`.
* [`MOZ_DEV_EDITION`](https://searchfox.org/mozilla-central/search?q=symbol%3AAppConstants%23MOZ_DEV_EDITION), which is used to restrict access to some advanced features.
* [`MOZ_TELEMETRY_REPORTING`](https://searchfox.org/mozilla-central/search?q=symbol:AppConstants%23MOZ_TELEMETRY_REPORTING) - used as an additional mean to disable telemetry.
* [`MOZ_CRASHREPORTER`](https://searchfox.org/mozilla-central/search?q=symbol:AppConstants%23MOZ_CRASHREPORTER) - disables crash reporting.
* [`MOZ_DATA_REPORTING`](https://searchfox.org/mozilla-central/search?q=symbol:AppConstants%23MOZ_DATA_REPORTING) - [disables initialization of data reporting system and disables recommendations](https://searchfox.org/mozilla-central/source/browser/components/preferences/privacy.js), 

Don't touch:
*  `MOZILLA_OFFICIAL` ([var](https://searchfox.org/mozilla-central/search?q=symbol%3AAppConstants%23MOZILLA_OFFICIAL), [macro](https://searchfox.org/mozilla-central/search?q=symbol:M_4924396bb8356f31)) - controls lots of different things. If you change it, your Firefox will fail to start.
* `MOZ_WEBEXT_WEBIDL_ENABLED` ([var](https://searchfox.org/mozilla-central/search?q=symbol:%23MOZ_WEBEXT_WEBIDL_ENABLED), [macro](https://searchfox.org/mozilla-central/search?q=symbol:M_MOZ_WEBEXT_WEBIDL_ENABLED)) - [requires compile-time changes in C++ part](https://searchfox.org/mozilla-central/source/toolkit/components/extensions/webidl-api/ExtensionBrowser.cpp#67).

## Thanks

This tool stands on the shoulders of giants.

### Dependencies

* https://github.com/Kronuz/esprima-python - for JS parsing
* https://github.com/ksons/jscodegen.py - for serializing JS back
* https://github.com/nih-at/libzip + [its python bindings](https://github.com/KOLANICH-libs/libzip.py) - for replacing files in zip archives. **ToDo: replace with a lib doing in-place**

### Sources of information

* https://old.reddit.com/r/ReverseEngineering/comments/51bxuv/modifying_release_builds_of_firefox_to_allow/d7arltj/
* https://github.com/zotero/zotero-standalone-build/blob/11e7c456732397d6b95b4b3a622990e50224b439/fetch_xulrunner.sh#L83-L90
* https://github.com/SebastianSimon/firefox-omni-tweaks
* https://github.com/xiaoxiaoflood/firefox-scripts/blob/master/installation-folder/config.js

