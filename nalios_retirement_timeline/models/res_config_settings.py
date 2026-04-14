# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    investment_product = fields.Many2one(
        "product.product",
        domain="[('type', '=', 'service')]",
        config_parameter="nalios_retirement_timeline.investment_product"
    )
    portal_folder = fields.Many2one(
        "documents.document",
        string="Default Portal Folder",
        domain=[('type', '=', 'folder')],
        config_parameter="nalios_retirement_timeline.default_portal_folder"
    )
