# -*- coding: utf-8 -*-
from odoo_xmlrpc_migration import odoo_xmlrpc_migration

plan = odoo_xmlrpc_migration()
plan.is_test = True

# 1
# plan.migrate('res.country')
# plan.migrate('res.country.state')
# plan.migrate('res.bank')

# plan.modules.append('product')
# plan.migrate('product.category')

# plan.modules.append('product')
# plan.migrate('product.product')

# después de migrar los productos
# plan.modules.append('product')
# plan.migrate('product.pricelist.item')
# plan.migrate('product.pricelist')

# n
# plan.migrate('res.partner')

# plan.migrate('res.users')

plan.modules.append('stock')
# plan.modules.append('sale_stock')
plan.modules.append('sale')
plan.modules.append('product')
plan.modules.append('uom')
# plan.migrate('sale.order', row_ids=[20020],default_country_id=10)
# plan.migrate('sale.order', row_ids=[19990],default_country_id=10)
# plan.migrate('sale.order.line')
plan.migrate('stock.picking', row_ids=[1070],default_country_id=10)
# plan.domain = [('id', '=', 927), ]
# plan.migrate('stock.move.line')