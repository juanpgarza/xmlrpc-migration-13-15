# -*- coding: utf-8 -*-
from odoo_xmlrpc_migration import odoo_xmlrpc_migration, mig_8_to_13, log_hash, modules_admin
import l10n_ar_methods

# pip3 install git+https://github.com/pysimplesoap/pysimplesoap@e1453f385cee119bf8cfb53c763ef212652359f5
# pip3 install git+https://github.com/ingadhoc/pyafipws@py3k

# IMPORTANTE este l10n_ar_reports lo tengo que instalar en un paso posterior porque me da error en 2 modelos

# Configurar:
#           activar moneda ARS (solo informar en la cia)
#           mostrar contabilidad completa

plan = odoo_xmlrpc_migration()
#plan.migrate('res.users', domain=[('active', '=', True), ('share', '=', False)])
plan.is_test = True

# plan.save_plan('account.payment.term')
# plan.save_plan('account.payment.term.line')
# plan.modules.append('account')
# plan.migrate('account.payment.term.line')
# plan.migrate('account.payment.term')
# PROBLEMA = cuando se crea un plazo se crea auto. una linea (con días en 0). Ent. al migrar se duplica la línea.
# ver si es necesario migrar y consultar con Filo

# plan.save_plan('stock.picking.type')
# plan.save_plan('stock.location')
# plan.save_plan('stock.move')
# plan.save_plan('stock.move.line')
# plan.save_plan('res.company')
# plan.save_plan('uom.uom')
plan.save_plan('stock.warehouse')
# stock.move.line

# product.category

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