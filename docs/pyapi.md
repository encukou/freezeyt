# Freezeyt's Python API

## Functions

### `freezeyt.freeze(app, config)`

### `freezeyt.freeze_async(app, config)`


## WSGI Middleware

### `freezeyt.Middleware`


## Hook Arguments

### `FreezeInfo`


#### `FreezeInfo.add_url(url, reason=None)`

Add the URL to the set of pages to be frozen.

If that URL was frozen already, or is outside the `prefix`, does nothing.

If you add a `reason` string, it will be used in error messages as the reason
why the added URL is being handled.

#### `FreezeInfo.add_hook(hook_name, callable)`

Register an additional hook function.

#### `FreezeInfo.total_task_count`

The number of pages `freezeyt` currently “knows about” –
ones that are already frozen plus ones that are scheduled to be frozen.

#### `FreezeInfo.done_task_count`

The number of pages that are done (either successfully
frozen, or failed).

#### `FreezeInfo.failed_task_count`

The number of pages that failed to freeze.

### `TaskInfo`  {: #TaskInfo }


### `TaskInfo.get_a_url()`:

Returns a URL of the page, including `prefix`.

Note that a page may be reachable via several URLs; this function returns
an arbitrary one.

### `TaskInfo.path`

The relative path the content is saved to.

### `TaskInfo.freeze_info`

A [`FreezeInfo`]{: #FreezeInfo } object corresponding to the entire
freeze process.

### `TaskInfo.exception`

For failed tasks, the exception raised. `None` otherwise.

### `TaskInfo.reasons`

A list of strings explaining why the given page was visited.
(Note that as the freezing progresses, new reasons may be added to
existing tasks.)

## Exceptions

### `freezeyt.VersionMismatch`

### `freezeyt.InfiniteRedirection`

### `freezeyt.ExternalURLError`

### `freezeyt.RelativeURLError`

### `freezeyt.UnexpectedStatus`

### `freezeyt.MultiError`

### `freezeyt.DirectoryExistsError`

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
