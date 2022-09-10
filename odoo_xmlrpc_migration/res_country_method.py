from . import odoo_xmlrpc_migration


def res_country_map_external_id(self):
    server = self.socks['from']
    sock = server['sock']
    args = [('model', '=', 'res.country')]
    return sock.execute(
        server['dbname'],
        server['uid'],
        server['pwd'],
        'ir.model.data',
        'search_read',
        args,
        ['complete_name', 'res_id', 'name']
    )

setattr(odoo_xmlrpc_migration, 'res_country_map_external_id', res_country_map_external_id)
