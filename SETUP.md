# Setup Guide

This repository contains the custom Odoo addon code for the Bookstore course project. It does not contain the local Odoo database, uploaded files, PostgreSQL credentials, pgAdmin settings, or the real `odoo.conf`.

## Start On Another Device

1. Install Odoo 17 and PostgreSQL on the new device.
2. Clone this repository:

   ```powershell
   git clone https://github.com/arberlilaj/odoo-course-project-bookstore.git
   ```

3. Copy `odoo.conf.example` to your local Odoo config location as `odoo.conf`.
4. Edit the copied `odoo.conf` for the new device:
   - set a new `admin_passwd`
   - set the local PostgreSQL `db_user` and `db_password`
   - update `addons_path` so it includes this repo's `Project` folder

   Example:

   ```ini
   addons_path = C:\Program Files\Odoo 17.0.20251003\server\addons,C:\Users\YOUR_USER\Documents\odoo-course-project-bookstore\Project
   ```

5. Start Odoo.
6. Open Apps, update the apps list, search for `Bookstore`, and install the module.

## Data Backup

The Git repo only saves code. If you also need the records created in Odoo, make a database backup from the original machine and restore it on the new one.

Do not commit database dumps or real config files to this repository.

## Learning Reference

The local `server/addons/commprog` folder was a separate cloned learning repository. It is not required for this Bookstore addon unless you intentionally want to study it again. The original source is listed in `REFERENCES.md`.
