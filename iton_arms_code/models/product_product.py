# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"
    _sql_constraints = [
        ('unique_arms_code', 'unique(arms_code)', 'Arms Code must be unique.'),
    ]

    arms_code = fields.Char(string="Arms Code", copy=False, index='btree_not_null')
    height = fields.Float('Height', digits='Stock Height')
    length = fields.Float('Length', digits='Stock Length')
    width = fields.Float('Width', digits='Stock Width')
    volume = fields.Float(compute="_compute_volume")

    @api.depends('length', 'width', 'height')
    def _compute_volume(self):
        for rec in self:
            rec.volume = (rec.length * rec.width * rec.height) / 1000000

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(ProductProduct, self).name_search(name=name, args=args, operator=operator, limit=limit)
        positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
        domain = args or []
        if operator in positive_operators:
            products = self.search_fetch(
                expression.AND([domain, [('arms_code', operator, name)]]),
                ['display_name'], limit=limit
            )
            if products:
                additional_products = [(p.id, p.display_name) for p in products]
                res.extend(additional_products)
        return res
