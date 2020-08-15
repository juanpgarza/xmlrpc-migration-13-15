# -*- coding: utf-8 -*-
from . import odoo_xmlrcp_migration
import hashlib


def map_hash(self, value, field, plan, row, field_collection='fields'):
    hash_key = 'lolo'
    string_to_hash = u"%s%s%s%s%s" % (hash_key,
                                      self.cache['external_ids']['res.users'][row['create_uid'][0]],
                                      row['create_date'],
                                      self.cache['external_ids']['res.users'][row['write_uid'][0]],
                                      row['write_date'])
    print (string_to_hash)
    return hashlib.new("sha1", string_to_hash.encode('utf-8')).hexdigest()


setattr(odoo_xmlrcp_migration, 'map_hash', map_hash)
