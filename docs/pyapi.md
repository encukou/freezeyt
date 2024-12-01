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

::: freezeyt.Config

A dictionary that holds [configuration][configuration] for Freezeyt.

## Actions

Built-in [actions][freeze-actions] are available as functions in
the ``freezeyt.actions`` module.
[Custom actions][custom-actions] should call one of these
functions and return its result.

::: freezeyt.actions.warn
::: freezeyt.actions.ignore
::: freezeyt.actions.follow
::: freezeyt.actions.save
::: freezeyt.actions.error

## URL finders

Built-in [URL finders][conf-url_finders] are available as
functions in the ``freezeyt.url_finders`` module:

::: freezeyt.url_finders.get_html_links
::: freezeyt.url_finders.get_html_links_async

::: freezeyt.url_finders.get_css_links
::: freezeyt.url_finders.get_css_links_async

::: freezeyt.url_finders.none

## Plugins

[Built-in plugins][built-in-plugins] are available in the
``freezeyt.plugins`` module:

::: freezeyt.plugins.ProgressBarPlugin
::: freezeyt.plugins.LogPlugin
::: freezeyt.plugins.GHPagesPlugin

## Utilities

::: freezeyt.url_to_path
