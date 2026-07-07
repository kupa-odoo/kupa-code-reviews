# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models


class AccountEdiXmlUblBlueKira(models.AbstractModel):
    _name = 'account.edi.xml.ubl.blue_kira'
    _inherit = 'account.edi.xml.cii'
    _description = "Blue Kira custom eInvoice (Factur-X with extra fields)"

    def _get_exchanged_document_vals(self, invoice):
        vals = super()._get_exchanged_document_vals(invoice)
        vals.update({
            'issuer_gln': invoice.company_id.partner_id.gln or '',
            'invoice_gln': invoice.partner_id.gln or '',
            'delivery_gln': invoice.partner_shipping_id.gln or '',
        })
        return vals

    def _export_invoice_vals(self, invoice):
        vals = super()._export_invoice_vals(invoice)
        for line_vals in vals['invoice_line_vals_list']:
            line = line_vals['line']
            customer_code = ''
            if invoice.partner_id and line.product_id and line.product_id.categ_id:
                category = line.product_id.categ_id
                partner_types = invoice.partner_id.partner_type_ids
                if partner_types:
                    code_record = category.client_code_ids.filtered(
                        lambda c: c.partner_type_id in partner_types
                    )
                    if code_record:
                        customer_code = code_record[0].code_client or ''
            line_vals['product_code'] = customer_code
        return vals

    def _export_invoice_filename(self, invoice):
        return f"{invoice.name.replace('/', '_')}_blue_kira.xml"
