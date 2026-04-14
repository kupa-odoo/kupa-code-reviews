# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    reimbursment_product = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'service')]
    )
    section_name = fields.Char()
