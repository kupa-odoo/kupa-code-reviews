# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    client_code_ids = fields.One2many(
        'product.category.client.code',
        'category_id',
        string='Codes Clients'
    )
