# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    gln = fields.Char(string="GLN")
    bluekira_number = fields.Char(string="Numéro fournisseur BlueKira")
    abbreviation = fields.Char(string="Abbréviation")
    invoice_edi_format = fields.Selection(
        selection_add=[('blue_kira', 'Blue Kira custom invoice')],
    )
    partner_type_ids = fields.Many2many(
        'partner.type',
        'res_partner_partner_type_rel',
        'partner_id',
        'type_id',
        string="Partner Types"
    )

    @api.model
    def _get_edi_builder(self, invoice_edi_format):
        if invoice_edi_format == 'blue_kira':
            return self.env['account.edi.xml.ubl.blue_kira']
        return super()._get_edi_builder(invoice_edi_format)

    @api.model
    def _get_ubl_cii_formats_info(self):
        res = super()._get_ubl_cii_formats_info()
        res['blue_kira'] = {
            'countries': ['FR'],
            'on_peppol': False,
        }
        return res
