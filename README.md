Bexio backend for Taxi
======================

This is the Bexio backend for [Taxi](https://github.com/sephii/taxi). It
exposes the `bexio` protocol to push entries to [Bexio](https://www.bexio.com).

Installation
------------

```shell
taxi plugin install bexio
```

Configuration
-------------

Run `taxi config` and use the `bexio` protocol for your backend :

```ini
[backends]
my_bexio_backend = bexio://[company_name]:[api_token]@api.bexio.com/?user=[user_id]&client_service=[client_service_id]&timesheet_status=[timesheet_status_id]
```

* `[company_name]`: an arbitrary company name (no space or anything weird), which is used to create the taxi project name
* `[api_token]`: which is generated by going to [admin/apiTokens](https://office.bexio.com/index.php/admin/apiTokens) (PS: it's very long)
* `[user_id]`: this is your user's ID, which can be found by going to [this page](https://office.bexio.com/index.php/billing/show/user_manager), click the "Manage user" button for your user,
 then look in the URL (it's something like `editRights/id/[N]`)
* `[client_service_id]`: this is the ID you wish to push timesheets to, which can be found by doing an API call to (replace `[api_token]` by your API token) :

```
curl --request GET \
  --url https://api.bexio.com/2.0/client_service \
  --header 'accept: application/json' \
  --header 'authorization: Bearer [api_token]'
```

* `[timesheet_status_id]`: this is the state you wish to use for the pushed timesheets, which can be found by doing an API call to (replace `[api_token]` by your API token) : 

```
curl --request GET \
  --url https://api.bexio.com/2.0/timesheet_status \
  --header 'accept: application/json' \
  --header 'authorization: Bearer [api_token]'
```

To generate taxi aliases for the projects, simply run `taxi update`.

Usage
-----

Let's say you used "FooBar" as the `[company_name]`.
Run `taxi alias list -b my_bexio_backend` (which lists all the projects added from Bexio), it should give you something like :

```
[my_bexio_backend] FOOBAR-2 -> FOOBAR/2 ([bexio] FooBar, .................)
... other similar entries ...
```

Now you can either directly add timesheet entries using the taxi alias part (`FOOBAR-2`) :

```
19/05/2020 # Tuesday
FOOBAR-2   08:00-09:00    Trying out taxi-bexio plugin
```

Or you could add custom taxi aliases by using the taxi project/activity part (`FOOBAR/1`).
Run `taxi config`, then append to the file :

```
[my_bexio_backend_aliases]
experiments = FOOBAR/1
```

Then use it like :

```
19/05/2020 # Tuesday
experiments   08:00-09:00    Trying out taxi-bexio plugin
```
