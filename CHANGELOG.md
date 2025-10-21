# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.3.0] - 2025-10-21

### Features

* Configuration may be specified in TOML format, using the `--toml-config` (`-t`)
  CLI option.
  The YAML format is still supported, but a new option name `--yaml-config` (`-y`)
  is preferred to the backwards-compatible name (`--config`, `-c`).
* For redirects, the message of `UnexpectedStatus` errors now shows the
  redirect target.

### Fixes

* For the `Freezeyt-URL-Finder` header, Using single word values (like `none`)
  now works as documented.
* The warning about multiple URLs being saved as the same file now deduplicates
  homepage URLs.
* The `--fail-fast` mode now fails faster.

### Python version support

* `freezeyt` now requires Python 3.8 or higher.
* `freezeyt` is now tested on Python 3.14.


## [1.2.0] - 2025-01-28

### Python version support

* `freezeyt` is now tested on Python 3.13.
* `freezeyt` is no longer tested on Python 3.7.
  (https://github.com/encukou/freezeyt/pull/405)

### Deprecations

* Deprecate extra pages starting with a slash. Extra page URLs should be
  relative to the prefix.
  (https://github.com/encukou/freezeyt/pull/406)

### Features

* When a page redirects to a page that would be saved to the same file
  (for example `/` to `/index.html`), save the target page regardless
  of general redirection settings.
  (https://github.com/encukou/freezeyt/issues/374)
* CLI options `app` and `output` now override configuration settings.
  (https://github.com/encukou/freezeyt/pull/407)
* Add `-h` CLI option, as an alias to `--help`
  (https://github.com/encukou/freezeyt/issues/394)
* Errors from infinite redirection loops are reported along with other
  page-specific errors. (https://github.com/encukou/freezeyt/pull/402)


## [1.1.1] - 2024-04-30

### Fixes

* The application supplied by the user is now passed to `extra_pages`
  generators. (https://github.com/encukou/freezeyt/issues/392)

## [1.1.0] - 2023-11-07

### Compatibility

* `freezeyt` is now tested on Python 3.11 and 3.12.
* `freezeyt` is now compatible with Werkzeug 3.0.

### Added

* The `Freezeyt-Action` HTTP header can now specify whether (and how) to freeze
  a page.
* The `Freezeyt-URL-Finder` HTTP header can now specify whether (and how)
  URLs to follow are found on a page.
* `Link` HTTP headers are now followed.
* `--fail-fast` option (`-x`, or `fail_fast` in config): stop freezing after
  the first error
* `gh_pages` plugin to simplify publishing to GitHub Pages
* `freezeyt.Middleware`: WSGI middleware that allows using some `freezeyt`
  features in dynamic web apps (even when not freezing)
* The application can be specified in configuration, not only as a CLI
  argument.
* `freezeyt.VersionMismatch`, the exception raised when the config format
  doesn't match the current `freezeyt` version

### Changed

* "Status_handlers" were renamed to "actions".
  The old name is still available and there are no plans to remove it.
* Backslashes in URL paths of extra files are now converted to forward slashes.
  A backslash can be inserted using the `%5c` escape sequence.

### Fixed

* The status handler configured for `2xx` now applies to `200 OK` statuses.
* Fixed handling edge cases in paths for extra files.

### Deprecated

* Multiple consecutive slashed in `prefix` are merged. `freezeyt` prints a
  warning when this happens.
* `freezeyt` now warns when multiple different URLs would be saved to a single
  file. There are no guarantees about which of the URLs is saved.


## [1.0] - 2022-05-03

Initial release.
