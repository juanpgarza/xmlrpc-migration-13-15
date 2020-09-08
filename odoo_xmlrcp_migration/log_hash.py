# -*- coding: utf-8 -*-
from . import odoo_xmlrcp_migration
import hashlib


HASH_REQ_COLUMNS = {'create_uid', 'create_date',
                    'write_uid', 'write_date'}


def map_hash(self, value, field, plan, row, field_collection='fields'):
    hash_key = 'lolo'
    if row.viewkeys() >= HASH_REQ_COLUMNS and row['create_uid'] and row['write_uid'] and \
            row['create_uid'][0] in self.cache['external_ids']['res.users'] and \
            row['write_uid'][0] in self.cache['external_ids']['res.users']:

        string_to_hash = u"%s%s%s%s%s" % (hash_key,
                                          self.cache['external_ids'][
                                              'res.users'][row['create_uid'][0]],
                                          row['create_date'],
                                          self.cache['external_ids'][
                                              'res.users'][row['write_uid'][0]],
                                          row['write_date'])
        return hashlib.new("sha1", string_to_hash.encode('utf-8')).hexdigest()
    print "no"
    return None


setattr(odoo_xmlrcp_migration, 'map_hash', map_hash)
