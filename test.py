# -*- coding: utf-8 -*-
from odoo_xmlrpc_migration import odoo_xmlrpc_migration, mig_8_to_13, log_hash, modules_admin
import l10n_ar_methods


plan = odoo_xmlrpc_migration()
#plan.migrate('res.users', domain=[('active', '=', True), ('share', '=', False)])
plan.is_test = True

plan.install_module('base_address_city')
plan.install_module('sale')
plan.install_module('l10n_ar')


plan.migrate('sale.order')

"""plan.install_module('crm')
plan.install_module('stock')

#

# base_address_city
# sale_management
plan.modules.append('order_validity')
plan.modules.append('stock')
plan.order = 'id desc'
# plan.save_plan('res.partner')
# plan.save_plan('res.partner.category')
# plan.migrate('res.partner.category')
# plan.migrate('res.country.state')
# plan.migrate('res.partner', default_country_id=10)
# plan.domain = [('id', '>', 3), ]
plan.migrate('res.users', domain=[
             ('active', '=', False), ('share', '=', False)])

# plan.modules.append('log_hash')
# plan.migrate('sale.order')

#row_ids = order_ids['write']+order_ids['create']
#plan.migrate('res.partner', domain=[('name', '!=', False)])

# print plan.cache['external_ids']
# plan.domain = [('id', '>', 134383), ]
# plan.migrate('res.partner')
"""