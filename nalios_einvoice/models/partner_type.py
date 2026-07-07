# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PartnerType(models.Model):
    _name = 'partner.type'
    _description = 'Type de client'

    name = fields.Char(string='Nom', required=True)
    partner_ids = fields.Many2many(
        'res.partner',
        'res_partner_partner_type_rel',
        'type_id',
        'partner_id',
        string="Partners"
    )
