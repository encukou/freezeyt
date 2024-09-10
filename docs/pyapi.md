# Freezeyt's Python API

## Functions


::: freezeyt.freeze

::: freezeyt.freeze_async


## WSGI Middleware

::: freezeyt.Middleware


## Hook Arguments

Objects of these classes are passed to custom [hooks][conf-hooks] and
[plugins][conf-plugins].

::: freezeyt.FreezeInfo

::: freezeyt.TaskInfo



## Exceptions

::: freezeyt.VersionMismatch
::: freezeyt.InfiniteRedirection
::: freezeyt.ExternalURLError
::: freezeyt.RelativeURLError
::: freezeyt.UnexpectedStatus
::: freezeyt.MultiError
::: freezeyt.DirectoryExistsError


## Types

### `freezeyt.Config`

## Actions

### `freezeyt.actions.warn`
### `freezeyt.actions.ignore`
### `freezeyt.actions.follow`
### `freezeyt.actions.save`
### `freezeyt.actions.error`

## URL finders

### `freezeyt.url_finders.get_html_links`
### `freezeyt.url_finders.get_html_links_async`

### `freezeyt.url_finders.get_css_links`
### `freezeyt.url_finders.get_css_links_async`

### `freezeyt.url_finders.none`

## Plugins

### `freezeyt.plugins.ProgressBarPlugin`
### `freezeyt.plugins.LogPlugin`
### `freezeyt.plugins.GHPagesPlugin`

## Utilities

### `freezeyt.url_to_path`
