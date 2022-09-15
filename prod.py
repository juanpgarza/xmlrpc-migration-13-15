# -*- coding: utf-8 -*-
from odoo_xmlrpc_migration import odoo_xmlrpc_migration

plan = odoo_xmlrpc_migration()
plan.is_test = False

# 1
plan.migrate('res.country')
plan.migrate('res.country.state')
plan.migrate('res.bank')

plan.modules.append('product')
plan.migrate('product.category')

plan.modules.append('product')
plan.migrate('product.product')

# después de migrar los productos
plan.modules.append('product')
plan.migrate('product.pricelist.item')
plan.migrate('product.pricelist')

# n
plan.migrate('res.partner')
