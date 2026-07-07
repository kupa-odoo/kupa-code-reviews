# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductCategoryClientCode(models.Model):
    _name = 'product.category.client.code'
    _description = 'Customer Codes for Product'

    category_id = fields.Many2one('product.category', string="Product Category")
    partner_type_id = fields.Many2one(
        'partner.type',
        string='Type de client',
    )
    code_client = fields.Char(string='Code client')
