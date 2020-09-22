from . import odoo_xmlrpc_migration


def map_sale_order_state(self, value, field, plan, row, field_collection='fields'):

    if value in ['gestionado', ' manual', 'progress', 'shipping_except']:
        return 'sent'
    return value

setattr(odoo_xmlrpc_migration, 'map_sale_order_state', map_sale_order_state)


def map_sale_order_state_line(self, value, field, plan, row, field_collection='fields'):

    if value in ['confirmed']:
        return 'sent'
    return value

setattr(odoo_xmlrpc_migration, 'map_sale_order_state_line',
        map_sale_order_state_line)


def map_product_type(self, value, field, plan, row, field_collection='fields'):

    if value != 'service':
        return 'consu'
    return value


setattr(odoo_xmlrpc_migration, 'map_product_type', map_product_type)



