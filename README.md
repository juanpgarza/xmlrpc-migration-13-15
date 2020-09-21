# Semi-automated Odoo migration process with XMLRPC

## Why Odoo migration needs to be automated as much as possible?
Migrating any ERP system is hard, Odoo included. We are not going to explain why. We only need to know that it is hard. The idea is; the Odoo upgrade work should focus on doing the new version deploy, how new workflows are performed and which new modules are installed. Odoo upgrade should not focus on how data is moved from one version to the next.
Odoo installations are different and highly customized. Each version removes or adds modules to the core (for instance, claim or city) or change module maintainer (product_pack). OpenUpgrade is a solution to this problem, but many modules do not have any support for this. Plus, OpenUpgrade requires you to migrate from version to the next version. Therefore, in order to migrate from version 8 to 13 you need to create 5 different sites and write and verify each of the 5 migrations of all the not supported modules (for instance, multiple localizations, product_pack, etc).

## How does it work?
Recursive migration process based on a python library that transfers data with XMLRPC and a repeatable, reusable migration plan that can be carried out in different stages. The migration steps are stored in yaml and python files. Why do we say it is a recursive process? Because in order to migrate sale orders, the process migrates sale order lines and products, users, sales teams… etc.


## Main ideas
* **ir.model.access:** Odoo model used to match the source and target records. We use the one in the target database.
* Migration plan: folder that holds all the migration related files (yaml and python files). You could have a different folder for each plan (8_13, 11_13, etc)
* **Modules:** a subfolder for each migrated module (not necessarily matches with an Odoo module)
* **Models:**  Models are yaml files that describe the source and target models, which fields to migrate (along with its names) and how to process the fields.
* **Script:** Set of instructions which are executed with the class odoo_xmlrpc_migration. One script is executed for every migration.

## Plan creation.
In order to start a plan you can run the following python instructions 
```python
from odoo_xmlrcp_migration import odoo_xmlrcp_migration


plan = odoo_xmlrcp_migration('/etc/odoo_xmlrcp_migration2.conf')
plan.save_plan('res.partner')
```

## Migration execution.
Source: my old Odoo site. 
Target: a fresh Odoo no data.
```python
from odoo_xmlrcp_migration import odoo_xmlrcp_migration
plan = odoo_xmlrcp_migration('/etc/odoo_xmlrcp_migration2.conf')

plan.test = True
plan.modules.append('l10n_ar')
plan.modules.append('city')
plan.modules.append('order_validity')
plan.migrate('sale.order')
```

## To-do:
* Load on the fly python modules, in order to execute python methods as needed
* Module in the target installation Odoo that allows you modify the audit information and blocks the creation messages
* Pip installation support
* Improvements to the plan creation
* Refactor code
* Invite community to contribute plans and modules.



