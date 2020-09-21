from . import odoo_xmlrpc_migration


def check_module_state(self, module, server='to'):
    server = self.socks[server]
    sock = server['sock']
    return sock.execute(
        server['dbname'],
        server['uid'],
        server['pwd'],
        'ir.module.module',
        'search_read',
        [('name', '=', module)],
        ['state']
    )


setattr(odoo_xmlrpc_migration, 'check_module_state', check_module_state)


def install_module(self, module, server='to'):
    module_state = self.check_module_state(module, server)
    if len(module_state) and module_state[0]['state'] == 'uninstalled':
        server = self.socks[server]
        sock = server['sock']
        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.module.module',
            'button_immediate_install',
            [module_state[0]['id']],
        )


setattr(odoo_xmlrpc_migration, 'install_module', install_module)
