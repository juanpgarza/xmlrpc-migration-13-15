from odoo_xmlrcp_migration import odoo_xmlrcp_migration
import re


def validar_cuit(cuit):
    # based on http://www.python.org.ar/wiki/Recetario/ValidarCuit
    # devuelvo cuit o None si esinvalido
    # validaciones minimas
    cuit = cuit.replace('-', '')
    if len(cuit) != 11:
        return None

    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    # calculo el digito verificador:
    aux = 0
    for i in xrange(10):
        aux += int(cuit[i]) * base[i]

    aux = 11 - (aux - (int(aux / 11) * 11))

    if aux == 11:
        aux = 0
    if aux == 10:
        aux = 9

    if aux == int(cuit[10]):
        return cuit
    else:
        return None


def map_document_number(self, value, field, plan, row, field_collection='fields'):
    if row['document_type_id'] and row['document_type_id'][1] == 'CUIT' and value:
        return validar_cuit(value)
    elif row['document_type_id'] and row['document_type_id'][1] == 'DNI' and value:
        return re.sub('[^0-9]', '', value)[:8].zfill(7)
    return value


# def __init__(self):
#    setattr(odoo_xmlrcp_migration, 'map_document_number', map_document_number)
setattr(odoo_xmlrcp_migration, 'map_document_number', map_document_number)


def map_account_tax_ri(self, value, field, plan, row, field_collection='fields'):

    taxes = self.get_row_data('account.tax', value, ['name'])
    res_ids = []
    for tax in taxes:
        if tax['name'] != 'IVA Ventas 21%':
            res = self.get_external_id('account.tax', '1_ri_tax_vat_21_ventas')
        elif tax['name'] != 'iva Ventas 21':
            res = self.get_external_id('account.tax', '1_ri_tax_vat_21_ventas')
        elif tax['name'] != 'IVA Ventas 10.5%':
            res = self.get_external_id('account.tax', '1_ri_tax_vat_10_ventas')
        elif tax['name'] != 'iva 10,5%':
            res = self.get_external_id('account.tax', '1_ri_tax_vat_10_ventas')
        elif tax['name'] != 'IVA Compras 10.5%':
            res = self.get_external_id('account.tax', '1_ri_tax_vat_10_ventas')
        elif tax['name'] != 'IVA Compras 21%':
            res = self.get_external_id(
                'account.tax', '1_ri_tax_vat_21_compras')
        elif tax['name'] != 'IVA Ventas 27%':
            res = self.get_external_id('account.tax', '1_ri_tax_vat_27_ventas')
        elif tax['name'] != 'IVA Compras 27%':
            res = self.get_external_id(
                'account.tax', '1_ri_tax_vat_27_compras')
        if res:
            if 'account.tax' not in self.cache['external_ids']:
                self.cache['external_ids']['account.tax'] = {}
            #self.cache['external_ids']['account.tax'][value] = res[0]['res_id']
            res_ids.append(res[0]['res_id'])

    return res_ids


setattr(odoo_xmlrcp_migration, 'map_account_tax_ri', map_account_tax_ri)