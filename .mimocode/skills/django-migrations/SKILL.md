---
name: django-migrations
description: Create and apply Django migrations, handling the stale summer_description RemoveField auto-detection
---

# Django Migrations (Katran)

## Create migrations

```powershell
$env:PYTHONPATH = "C:\Users\KDGHome\katran\env\Lib\site-packages"
.\env\Scripts\python.exe manage.py makemigrations <app> --name <name>
```

## Stale RemoveField gotcha

Django auto-detects removal of `summer_description` from Category (field was removed from model but never from DB). This generates a `RemoveField` operation in **every new store migration**. 

**Always check** the generated migration file for `RemoveField` operations on `summer_description` and **remove them manually** before applying.

This has happened in migrations 0057, 0058, 0059, and will keep happening until the column is actually dropped from the database.

## Apply migrations

```powershell
$env:PYTHONPATH = "C:\Users\KDGHome\katran\env\Lib\site-packages"
.\env\Scripts\python.exe manage.py migrate
```

## Check migration status

```powershell
$env:PYTHONPATH = "C:\Users\KDGHome\katran\env\Lib\site-packages"
.\env\Scripts\python.exe manage.py showmigrations
```
