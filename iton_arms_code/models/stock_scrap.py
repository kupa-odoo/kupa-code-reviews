# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    arms_code = fields.Char(related='product_id.arms_code', readonly=False, related_sudo=False)
