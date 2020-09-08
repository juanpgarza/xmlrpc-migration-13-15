from odoo_xmlrcp_migration import odoo_xmlrcp_migration


plan = odoo_xmlrcp_migration('/etc/odoo_xmlrcp_migration.conf')
plan.save_plan('account.tax')

"""plan.save_plan('res.users')
plan.save_plan('res.partner')
plan.save_plan('sale.order')
plan.save_plan('sale.order.line')

plan.save_plan('product.product')
plan.save_plan('product.template')
plan.save_plan('product.pricelist')
plan.save_plan('crm.case.section', 'crm.team')
plan.save_plan('product.uom.categ', 'uom.category')
plan.save_plan('res.country')
plan.save_plan('res.country.state')
plan.save_plan('res.country.state.city', 'res.city')

"""

#plan.save_plan('res.partner.category')
#plan.save_plan('stock.rule')

"""
plan.save_plan('stock.warehouse')
plan.save_plan('stock.picking')
plan.save_plan('stock.location')
plan.save_plan('account.invoice').line
plan.save_plan('product.public').category
plan.save_plan('product.attribute').line
plan.save_plan('stock.warehouse').orderpoint
plan.save_plan('account.tax')
plan.save_plan('product.supplierinfo')
plan.save_plan('stock.location')
plan.save_plan('stock.location').route
plan.save_plan('account.journal')
"""