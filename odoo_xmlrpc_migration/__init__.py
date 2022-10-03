from configparser import ConfigParser
from xmlrpc import client as xmlrpclib
from ast import literal_eval
import yaml
import os

from inspect import getouterframes, currentframe, stack

import logging
logging.basicConfig(level=logging.INFO)


class odoo_xmlrpc_migration(object):
    socks = {}
    modules = ['base']
    domain = []
    chunk_size = 100
    company_id = 1
    is_test = False
    update = True
    create = True
    cache = {'plans': {}, 'external_ids': {}}
    max_stack = 40
    system_fields = ['id', 'write_date', 'write_uid',
                     'create_date', 'create_uid', '__last_update']
    order = 'id asc'
    context = {}
    active_list = ['|', ('active','=', True),('active','=', False)]
    def __init__(self, config_file='/home/juan/filo-migration/xmlrpc_migration/test.conf'):
        self.config = ConfigParser()
        self.config.read(config_file)
        self.data_dir = self.config.get("yalm", 'path')
        self.socks['from'] = {
            'dbname': self.config.get("odooserver_1", 'dbname'),
            'username': self.config.get("odooserver_1", 'username'),
            'pwd': self.config.get("odooserver_1", 'pwd'),
            'url': self.config.get("odooserver_1", 'url'),
        }
        self.socks['from']['sock_common'] = xmlrpclib.ServerProxy(
            self.socks['from']['url'] + 'xmlrpc/common')

        self.socks['from']['uid'] = self.socks['from']['sock_common'].login(
            self.socks['from']['dbname'],
            self.socks['from']['username'],
            self.socks['from']['pwd']
        )
        self.socks['from']['sock'] = xmlrpclib.ServerProxy(
            self.socks['from']['url'] + 'xmlrpc/object')
        
        self.socks['to'] = {
            'dbname': self.config.get("odooserver_2", 'dbname'),
            'username': self.config.get("odooserver_2", 'username'),
            'pwd': self.config.get("odooserver_2", 'pwd'),
            'url': self.config.get("odooserver_2", 'url'),
        }
        self.socks['to']['sock_common'] = xmlrpclib.ServerProxy(
            self.socks['to']['url'] + 'xmlrpc/common')

        self.socks['to']['uid'] = self.socks['to']['sock_common'].login(
            self.socks['to']['dbname'],
            self.socks['to']['username'],
            self.socks['to']['pwd']
        )
        self.socks['to']['sock'] = xmlrpclib.ServerProxy(
            self.socks['to']['url'] + 'xmlrpc/object')

    def clean_cache(self):
        self.cache = {'plans': {}, 'external_ids': {}}

    def xfields_get(self, server, model):
        server = self.socks[server]
        sock = server['sock']
        return sock.execute(server['dbname'], server['uid'], server['pwd'], model, 'fields_get')

    def fields_get(self, server, model, ignore_readonly=False):
        server = self.socks[server]
        sock = server['sock']
        leaf = [('model_id.model', '=', model),
                ('name', 'not in', self.system_fields)]
        if ignore_readonly:
            leaf += [('readonly', '=', False)]
        f = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.fields',
            'search_read',
            leaf, []
        )

        return {x['name']: x for x in f}

    def compare_model(self, model_from, model_to=False):
        fields = {}
        no_match_fields = {}
        model_to = model_to if model_to else model_from
        fields_from = self.fields_get('from', model_from)
        fields_to = self.fields_get('to', model_to, True)
        keys_from = set(fields_from.keys())
        keys_to = set(fields_to.keys())
        intersection = keys_from & keys_to
        for field in list(intersection):
            if fields_from[field]['modules'] not in fields:
                # to-do: defaultdict ?
                fields[fields_from[field]['modules']] = {}
            # if not fields_to[field].get('store', True):
            #    continue
            fields[fields_from[field]['modules']][
                field] = self.dump_config_field(field, fields_from, fields_to)
        diff = keys_from - keys_to
        for field in list(diff):

            if fields_from[field]['modules'] not in no_match_fields:
                # to-do: defaultdict ?
                no_match_fields[fields_from[field]['modules']] = {}
            # if not fields_to[field].get('store', True):
            #    continue
            no_match_fields[fields_from[field]['modules']][
                field] = self.dump_config_field(field, fields_from, fields_to)

        return fields, no_match_fields

    def dump_config_field(self, field, fields_from, fields_to):
        field_temp = {}
        if field in fields_from:
            field_temp['from'] = {'name': field,
                                  'type': fields_from[field]['ttype']}
            if fields_from[field]['relation']:
                field_temp['from']['relation'] = fields_from[field]['relation']
            if fields_from[field]['relation_field']:
                field_temp['from']['relation_field'] = fields_from[
                    field]['relation_field']

        if field in fields_to:
            field_temp['to'] = {'name': field,
                                'type': fields_to[field]['ttype']}

            if fields_to[field]['relation']:
                field_temp['to']['relation'] = fields_to[field]['relation']
            if fields_to[field]['relation_field']:
                field_temp['to']['relation_field'] = fields_to[
                    field]['relation_field']
        if field in fields_to and field in fields_from:
            if fields_to[field]['ttype'] == fields_to[field]['ttype']:
                field_temp['map_method'] = 'magic_map'
            else:
                field_temp['map_method'] = '%s2%s' % (
                    fields_from[field]['ttype'] == fields_from[field]['ttype'])
        return field_temp

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_plan(self, model_from, model_to=False, ignore_module=False):
        model_to = model_to if model_to else model_from
        data = {}
        data['model_from'] = model_from
        data['model_to'] = model_to
        data['domain'] = []
        data['external_id_nomenclature'] = model_from.replace('.', '_') + "_%s"
        data['external_id_method'] = 'row_get_id'
        fields_by_module, no_match_fields = self.compare_model(
            model_from, model_to)
        model_name = model_from.replace('.', '_')
        for module in fields_by_module:
            data['fields'] = fields_by_module[
                module] if module in fields_by_module else []
            data['no_match_fields'] = no_match_fields[
                module] if module in no_match_fields else []
            file_name = '%s/%s/%s.yaml' % (self.data_dir, module, model_name)
            self.ensure_dir(file_name)
            with open(file_name, 'w+') as file:
                yaml.dump(data, file)

    def load_plan(self, model_from):
        # import pdb; pdb.set_trace()
        model_name = model_from.replace('.', '_')
        if model_name in self.cache['plans']:
            return self.cache['plans'][model_name]
        result = {}
        # import pdb; pdb.set_trace()
        for module in self.modules:
            try:
                # import pdb; pdb.set_trace()
                with open('%s/%s/%s.yaml' % (self.data_dir, module, model_name)) as file:
                    # data = yaml.full_load(file)
                    data = yaml.load(file, Loader=yaml.FullLoader)
                    if not len(result):
                        result = data
                    else:
                        result['fields'].update(data['fields'])
                        result['domain'] += data['domain']
                    # import pdb; pdb.set_trace()
            except IOError:
                pass
                # import pdb; pdb.set_trace()
        # import pdb; pdb.set_trace()
        if len(result) == 0:
            print("Not exists plan for %s" % model_from)
            # logging.debug("Not exists plan for %s" % model_from)
        self.cache['plans'][model_name] = result
        return result

    def get_context(self, **kwargs):
        return kwargs['context'] if 'context' in kwargs else {}

    def get_fields(self, plan, model_name, kwargs):
        field_names = plan['fields'].keys()
        after_save_fields = list(plan['after_save_fields'].keys()) if 'after_save_fields' in plan else []

        if 'force_fields' in kwargs:
            logging.debug("fuerzo %s de %s " % (kwargs['force_fields'], model_name))
            field_names = kwargs['force_fields']

        if 'only_fields' in kwargs:
            self.create = False
            logging.debug("Solo migro %s de %s " % (kwargs['only_fields'], model_name))
            field_names = {x: plan['fields'][x] for x in kwargs['only_fields'] if x in field_names}

            if after_save_fields: 
                after_save_fields =  {x: plan['after_save_fields'][x] for x in kwargs['only_fields'] if x in after_save_fields}
            if not field_names and after_save_fields:
                field_names = after_save_fields
                after_save_fields = []

        if 'ignore_field' in kwargs and kwargs['ignore_field'] in field_names:
            #print("remuevo %s de %s " % (kwargs['ignore_field'], model_name))
            logging.debug("remuevo %s de %s " % (kwargs['ignore_field'], model_name))
            field_names.remove(kwargs['ignore_field'])
        return field_names, after_save_fields

    def get_row_ids(self, plan, kwargs):
        if 'row_ids' in kwargs:
            row_ids = kwargs['row_ids']
        else:
            model_domain = kwargs['domain'] if 'domain' in kwargs else []
            row_ids = self.get_ids(plan['model_from'], plan[
                                   'domain'] + model_domain + self.domain)
        return row_ids




    def migrate(self, model_name, **kwargs):
        plan = self.load_plan(model_name)
        res_ids = {'create': [], 'write': []}
        # import pdb; pdb.set_trace()
        field_names, after_save_fields = self.get_fields(plan, model_name, kwargs)
        row_ids = self.get_row_ids(plan, kwargs)
        chunk = [row_ids[i:i + self.chunk_size]
                 for i in range(0, len(row_ids), self.chunk_size)]
        old_field_names = field_names
        field_names = []
        for field_name in old_field_names:
            field_names.append(field_name)
        # import pdb; pdb.set_trace()
        for ids in chunk:
            rows = self.read(plan['model_from'], ids,
                             field_names + after_save_fields)
            # import pdb; pdb.set_trace()
            for row in rows:
                # import pdb; pdb.set_trace()
                data = self.map_data(plan, row, kwargs)
                # import pdb; pdb.set_trace()
                action, model, res_id = self.save(plan, data, row['id'], kwargs)
                # import pdb; pdb.set_trace()
                res_ids[action].append(res_id)
                if len(after_save_fields) and res_id:
                    data = self.map_data(
                        plan, row, kwargs, 'after_save_fields')
                    kwargs_after = kwargs.copy()
                    if isinstance(res_id, int):
                        kwargs_after['res_id'] = res_id 
                    else:
                        kwargs_after['res_id'] = res_id[0]['res_id']

                    self.save(plan, data, row['id'], kwargs_after)

            if self.is_test:
                return res_ids
        return res_ids

    def save(self, plan, values, orig_id, kwargs):
        update = self.update
        create = self.create
        res_id = kwargs.get('res_id', False)
        server = self.socks['to']
        sock = server['sock']
        if res_id:
            try:
                sock.execute_kw(
                        server['dbname'],
                        server['uid'],
                        server['pwd'],
                        plan['model_to'],
                        'write',
                        [[res_id],
                        values],
                        {'context': self.context}

                    )
    
                return ('write', plan['model_to'], res_id)
            except xmlrpclib.Fault as e:
                logging.error(e.faultCode)
                return ('write', plan['model_to'], False)
        external_id_method = getattr(self, plan['external_id_method'])
        xt_id = plan['external_id_nomenclature'] if 'external_id_nomenclature' in plan else False

        if 'external_id_company_prefix' in plan:
            xt_id = str(self.company_id) + '_' + xt_id
        ext_id = external_id_method(
            plan, orig_id, xt_id)

        if ext_id and len(ext_id):            
            if update is False: 
                logging.debug("Ignoro update de %s " % ext_id)

                return ('write', plan['model_to'], False)
            try:
                sock.execute_kw(
                    server['dbname'],
                    server['uid'],
                    server['pwd'],
                    plan['model_to'],
                    'write',
                    [[ext_id[0]['res_id']],
                     values],
                    {'context': self.context}

                )
                logging.info('Writing %s %s' % (plan['model_to'], ext_id[0]['res_id']))
                return ('write', plan['model_to'], ext_id)
            except xmlrpclib.Fault as e:
                # import pdb; pdb.set_trace()
                logging.error(e.faultCode)
                return ('write', plan['model_to'], False)

        else:
            # import pdb; pdb.set_trace()
            if create is False:
                logging.debug("Ignoro creacion de %s " % orig_id)
                return ('create', plan['model_to'], False)

            try:
                res_id = sock.execute_kw(
                    server['dbname'],
                    server['uid'],
                    server['pwd'],
                    plan['model_to'],
                    'create',
                    [values],
                    {'context': self.context}
                )
                logging.info('Creating %s %s' % (plan['model_to'], res_id))
                if plan['external_id_method'] == 'row_get_id':
                    self.add_external_id(plan['model_to'], orig_id, res_id, plan['external_id_nomenclature'])
                return ('create', plan['model_to'], res_id)
            except xmlrpclib.Fault as e:
                #print(e.faultCode)
                # import pdb; pdb.set_trace()
                logging.debug(e.faultCode)
                return ('create', plan['model_to'], False)

    def get_ids(self, model, domain):
        server = self.socks['from']
        sock = server['sock']
        return sock.execute(server['dbname'], server['uid'], server['pwd'], model, 'search',
                            domain, 0, False, self.order
                            )

    def search_read(self, model, leaf, fields, dir='from'):
        server = self.socks[dir]
        sock = server['sock']
        #print('Reading %s %s %s'%(server,model,ids))
        #logging.debug('Reading  %s %s'%(model,ids))

        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            model,
            'search_read',
            leaf,
            fields
        )


    def read(self, model, ids, fields, dir='from'):
        server = self.socks[dir]
        sock = server['sock']
        #print('Reading %s %s %s'%(server,model,ids))
        #logging.debug('Reading  %s %s'%(model,ids))

        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            model,
            'read',
            ids,
            fields
        )

    def get_default(self, field, kwargs):
        return kwargs.get('default_%s' % field, None)

    def map_data(self, plan, row, kwargs, field_collection='fields'):
        maping = {}
        for field in plan[field_collection]:
            f = plan[field_collection][field]
            if f['from']['name'] not in row:
                continue
            map_method = getattr(
                self, f['map_method'] if 'map_method' in f else 'magic_map')
            val = map_method(row[f['from']['name']], field,
                             plan, row, field_collection)
            default_value = self.get_default(field, kwargs)
            if val is not None or default_value is not None:
                maping[f['to']['name']] = val if val is not None else default_value
        return maping

    def map_fix_value(self, value, field, plan, row, field_collection='fields'):
        field_data = plan[field_collection][field]
        return field_data['to']['value']

    def fix_value_map(self, value, field, plan, row, field_collection='fields'):
        field_data = plan[field_collection][field]

        if field_data['to']['type'] == 'date':
            return field_data['to']['value'].strftime("%Y-%m-%d")
        elif field_data['to']['type'] == 'datetime':
            return field_data['to']['value'].strftime("%Y-%m-%d %H:%M:%S")
        elif field_data['to']['type'] in ['decimal', 'float']:
            return float(field_data['to']['value'])
        elif field_data['to']['type'] in ['boolean']:
            return bool(field_data['to']['value'])
        elif field_data['to']['type'] in ['selection',
                                          'char', 'float', 'integer',
                                          'text', 'html', 'boolean']:
            return str(field_data['to']['value'])
        elif field_data['to']['type'] in ['many2many', 'one2many']:
            return literal_eval(field_data['to']['value'])


    def magic_map(self, value, field, plan, row, field_collection='fields'):
        field_data = plan[field_collection][field]
        if field_data['to']['type'] in ['selection', 'date', 'datetime',
                                          'char', 'float',
                                          'text', 'html', 'boolean']:
            # to-do : Cast Value type
            return value
        elif field_data['to']['type'] == 'integer':
            return int(value)
        elif field_data['from']['type'] == 'one2many':
            subplan = self.load_plan(field_data['from']['relation'])
            if not subplan:
                return None
            external_id_method = getattr(self, subplan['external_id_method'])
            res_ids = []
            for res_id in value:
                ext_id = external_id_method(subplan, res_id, row)
                if len(ext_id):
                    res_ids.append(ext_id[0]['res_id'])
                else:
                    if field_data.get('required', False):
                        ignore_field = field_data['from']['relation_field']
                    else:
                        ignore_field = False
                    new = self.migrate(
                        field_data['from']['relation'],
                        row_ids=[res_id],
                        ignore_field=ignore_field

                    )
                    if len(new['create']):
                        res_ids.append(new['create'][0])
                    else:
                        return None
            return [(6, 0, res_ids)]

        elif field_data['from']['type'] in ['many2one'] and value:
            subplan = self.load_plan(field_data['from']['relation'])
            if len(subplan) == 0:
                return None
            external_id_method = getattr(self, subplan['external_id_method'])
            # import pdb; pdb.set_trace()
            ext_id = external_id_method(
                subplan, value[0], row, field_data.get('cache', False))
            if ext_id and len(ext_id):
                return ext_id[0]['res_id']
            else:
                if len(stack(0)) > 20:
                    return None

                new = self.migrate(
                    field_data['from']['relation'],
                    row_ids=[value[0]]
                )
                if len(new['create']):
                    return new['create'][0]
                else:
                    return None

        elif field_data['from']['type'] in ['many2many']:
            subplan = self.load_plan(field_data['from']['relation'])
            if not subplan:
                return None
            external_id_method = getattr(self, subplan['external_id_method'])
            res_ids = []
            for res_id in value:
                ext_id = external_id_method(subplan, res_id, row)
                if ext_id and len(ext_id):
                    res_ids.append(ext_id[0]['res_id'])
                else:
                    new = self.migrate(
                        field_data['from']['relation'],
                        row_ids=[res_id]
                    )
                    res_ids.append(new['create'][0])
            if not len(res_ids):
                return None
            return [(6, 0, res_ids)]

        return None

    def other_row_get_first_id(self, plan, value, row, cache=False):
        raise('ooo')
        server = self.socks['to']
        sock = server['sock']
        company_prefix = ''
        if 'external_id_company_prefix' in plan:
            company_prefix = str(self.company_id) + '_'
        row_value = row[plan['match_field']][0] 
        nomeclature = company_prefix + plan['external_id_nomenclature']
        args = [('name', '=', nomeclature % row_value),
                ('module', '=', 'xmlrpc_migration'),
                ('model', '=', plan['model_to'])]

        res = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'search_read',
            args,
            ['res_id']
        )

        if len(res):
            record = sock.execute(
                server['dbname'],
                server['uid'],
                server['pwd'],
                plan['model_to'],
                'search',
                [(plan['match_field'],'=',res[0]['res_id'])],

            )
            if len(record):
                return [{'res_id':record[0]}]

        return False

    def row_get_id(self, plan, value, row, cache=False):
        server = self.socks['to']
        sock = server['sock']
        company_prefix = ''
        if 'external_id_company_prefix' in plan:
            company_prefix = str(self.company_id) + '_'
        nomeclature = company_prefix + plan['external_id_nomenclature']
        args = [('name', '=', nomeclature % value),
                ('module', '=', 'xmlrpc_migration'),
                ('model', '=', plan['model_to'])]

        res = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'search_read',
            args,
            ['res_id']
        )

        if cache and len(res):
            if plan['model_from'] not in self.cache['external_ids']:
                self.cache['external_ids'][plan['model_from']] = {}
            self.cache['external_ids'][plan['model_from']][
                value] = res[0]['res_id']

        return res

    def add_external_id(self, model, orig_id, dest_id, nomeclature):
        server = self.socks['to']
        sock = server['sock']
        vals = [{
                'name': nomeclature % orig_id,
                'module': 'xmlrpc_migration',
                'model': model,
                'res_id': dest_id,
                'noupdate': True
                }]

        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'create',
            vals
        )

    def same_name(self, plan, res_id, row, cache=False):
        server = self.socks['from']
        sock = server['sock']
        external_id = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'search',
            [('name', '=', row['name'])]
        )
        if len(external_id):
            return [{'res_id':external_id[0]}]
            if cache:
                if plan['model_from'] not in self.cache['external_ids']:
                    self.cache['external_ids'][plan['model_from']] = {}
                self.cache['external_ids'][plan['model_from']][
                    res_id] = external_id[0]
            return res

        return None


    def same_external_id(self, plan, res_id, row, cache=False):
        server = self.socks['from']
        sock = server['sock']
        external_id = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'search_read',
            [('res_id', '=', res_id), ('model', '=', plan['model_from'])],
            ['complete_name', 'res_id', 'name']
        )
        if len(external_id):
            server = self.socks['to']
            sock = server['sock']
            res = sock.execute(
                server['dbname'],
                server['uid'],
                server['pwd'],
                'ir.model.data',
                'search_read',
                [('name', '=', external_id[0]['name']),
                 ('model', '=', plan['model_to'])],
                ['res_id']
            )
            if cache:
                if plan['model_from'] not in self.cache['external_ids']:
                    self.cache['external_ids'][plan['model_from']] = {}
                self.cache['external_ids'][plan['model_from']][
                    res_id] = res[0]['res_id']
            return res

        return None

    def get_external_id(self, model, external_id, server='to'):
        server = self.socks[server]
        sock = server['sock']
        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'search_read',
            [('name', '=', external_id), ('model', '=', model)],
            ['res_id']
        )

    def match_field(self, plan, res_id, row, cache=False):
        server = self.socks['from']
        sock = server['sock']
        external_field_value = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            plan['model_from'],
            'read',
            [res_id],
            [plan['external_id_field_from']]
        )
        if len(external_field_value):

            server = self.socks['to']
            sock = server['sock']
            leaf = [(plan['external_id_field_to'], '=', external_field_value[
                     0][plan['external_id_field_from']])]
            if 'active' in plan['fields'].keys():
                leaf += ['|', ('active', '=', False), ('active', '=', True)]
            if 'external_id_domain_to' in plan:
                leaf += plan['external_id_domain_to']
            external_id = sock.execute(
                server['dbname'],
                server['uid'],
                server['pwd'],
                plan['model_to'],
                'search',
                leaf
            )
            if len(external_id):
                if cache:
                    if plan['model_from'] not in self.cache['external_ids']:
                        self.cache['external_ids'][plan['model_from']] = {}
                    self.cache['external_ids'][plan['model_from']][
                        res_id] = external_id[0]

                return [{'res_id': external_id[0]}]
        return None

    def get_row_data(self, model, res_ids, fields=[], server='from'):
        server = self.socks[server]
        sock = server['sock']
        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            model,
            'read',
            res_ids,
            fields
        )

    def execute_method_chunked(self, model, method, ids, server='from'):
        server = self.socks[server]
        sock = server['sock']
        chunks = [ids[i:i + self.chunk_size - 1]
                  for i in range(0, len(ids), self.chunk_size)]
        for chunk in chunks:
            print ("execute %s: %s of %s" % (method, len(chunk), len(chunks)))
            sock.execute(
                server['dbname'],
                server['uid'],
                server['pwd'],
                model,
                method,
                chunk
            )
        return True

    def search(self, model, leaf,  server='from'):
        server = self.socks[server]
        sock = server['sock']
        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            model,
            'search',
            leaf
        )

    def get_parameter(self, key, default_value):
        server = self.socks['to']
        sock = server['sock']
        exist = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.config_parameter',
            'search',
            [('key', '=', key)],
        )
        if len(exist):
            exist = sock.execute(
                        server['dbname'],
                        server['uid'],
                        server['pwd'],
                        'ir.config_parameter',
                        'read',
                        exist,
                        ['value']
                    )
            return exist[0]['value']
        return default_value

    def set_parameter(self, key, value):
        server = self.socks['to']
        sock = server['sock']
        exist = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.config_parameter',
            'search',
            [('key', '=', key)]
        )
        if len(exist):
            return sock.execute(
                server['dbname'],
                server['uid'],
                server['pwd'],
                'ir.config_parameter',
                'write',
                exist,
                {'value': str(value)}
            )
        return sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.config_parameter',
            'create',
            [{
                'key': key,
                'value': str(value)
            }]
        )

    def same_name_many2one(self, value, field, plan, row, field_collection='fields'):
        field_data = plan[field_collection][field]

        server = self.socks['to']
        sock = server['sock']
        ext_id = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            field_data['to']['relation'],
            'search',
            [('name', '=', value[1])],
        )
        if len(ext_id):
            return ext_id[0]
        else:
            if len(stack(0)) > 20:
                return None

            new = self.migrate(
                field_data['from']['relation'],
                row_ids=[value[0]]
            )
            if len(new['create']):
                return new['create'][0]
            else:
                return None

    def same_value(self, value, field, plan, row, field_collection='fields'):
        field_data = plan[field_collection][field]

        server = self.socks['to']
        sock = server['sock']

        ext_id = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            field_data['to']['relation'],
            'search',
            [('name', '=', value[1])],
        )
        if len(ext_id):
            return ext_id[0]
        else:
            if len(stack(0)) > 20:
                return None

            new = self.migrate(
                field_data['from']['relation'],
                row_ids=[value[0]]
            )
            if len(new['create']):
                return new['create'][0]
            else:
                return None

    def get_result_ids(self, result_set):
        new = [x for x in result_set['create']]
        updated = [x[0]['res_id'] for x in result_set['write']]
        return new + updated


    def name_field_def(self):
        return {'name':{'from':{'name': 'name','type': 'char'},'to':{'name': 'name','type': 'char'}}}


    def env_company_id(self, value, field, plot, row, field_collection='fields'):
        return self.company_id

    def get_cache(self, model_from, org_id):
        if model_from not in self.cache['external_ids']:
            self.cache['external_ids'][model_from] = {}
            if org_id in self.cache['external_ids'][model_from]:
                return self.cache['external_ids'][model_from]['org_id']

    def set_cache(self, model_from, org_id, dest_id):
        if model_from not in self.cache['external_ids']:
            self.cache['external_ids'][model_from] = {}
        self.cache['external_ids'][model_from][org_id] = dest_id

    def migrate_inverse(self, model_name, **kwargs):
        server = self.socks['to']
        sock = server['sock']

        plan = self.load_plan(model_name)

        ids = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            plan['model_to'],
            'search',
            kwargs['domain']
        )
        if len(ids):
            args = [('res_id', 'in', ids),
                    ('module', '=', 'xmlrpc_migration'),
                    ('model', '=', plan['model_to'])]

            res = sock.execute(
                server['dbname'],
                server['uid'],
                server['pwd'],
                'ir.model.data',
                'search_read',
                args,
                ['name']
            )

            map_ids = [int(x['name'].split('_')[-1]) for x in res]
            if map_ids:
                self.migrate(model_name,row_ids=map_ids)

    def detect_new(self, model_name, **kwargs):
        plan = self.load_plan(model_name)
        row_ids = self.get_row_ids(plan, kwargs)
        chunks = [row_ids[i:i + self.chunk_size]
                 for i in range(0, len(row_ids), self.chunk_size)]

        external_id_method = getattr(self, plan['external_id_method'] + '_multiple')
        xt_id = plan['external_id_nomenclature'] if 'external_id_nomenclature' in plan else False
        if 'external_id_company_prefix' in plan:
            xt_id = str(self.company_id) + '_' + xt_id

        for chunk in chunks:
            res_ids = external_id_method(plan, chunk, xt_id)
            print ("Migrando %s %s" % (len(res_ids),model_name,)) 
            new = self.migrate(
                model_name,
                row_ids=res_ids,
            )

    def row_get_id_multiple(self, plan, ids, nomeclature):
        server = self.socks['to']
        sock = server['sock']
        names = {nomeclature % value : value for value in ids }


        args = [('name', 'in', list(names.keys())),
                ('module', '=', 'xmlrpc_migration'),
                ('model', '=', plan['model_to'])]

        res = sock.execute(
            server['dbname'],
            server['uid'],
            server['pwd'],
            'ir.model.data',
            'search_read',
            args,
            ['name']
        )
        map_names = [x['name'] for x in res]
        ret = []
        for name in names :
            if name not in map_names:
                ret.append(names[name])
        return ret
