from . import odoo_xmlrpc_migration




def update_module_list(self,  server='to'):
    server = self.socks[server]
    sock = server['sock']
    return sock.execute(
        server['dbname'],
        server['uid'],
        server['pwd'],
        'ir.module.module',
        'update_list'
        )


setattr(odoo_xmlrpc_migration, 'update_module_list', update_module_list)




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
        print ('Instalar modulo %s ' % module) 
        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.module.module',
            'button_immediate_install',
            [module_state[0]['id']],
        )
    if len(module_state) == 0:
        print ('El modulo %s no esta disponible' % module) 


setattr(odoo_xmlrpc_migration, 'install_module', install_module)
