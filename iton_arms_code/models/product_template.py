# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = "product.template"

    arms_code = fields.Char(
        string="Arms Code",
        compute="_compute_arms_code",
        inverse='_set_arms_code',
        search='_search_arms_code'
    )
    length = fields.Float(
        'Length', compute='_compute_length', digits='Stock Length',
        inverse='_set_length', store=True)
    height = fields.Float(
        'Height', compute='_compute_height', digits='Stock Height',
        inverse='_set_height', store=True)
    width = fields.Float(
        'Width', compute='_compute_weight', digits='Stock Width',
        inverse='_set_width', store=True)

    lhw_uom_name = fields.Char(string='Length, Height, Width unit of measure label', compute='_compute_lhw_uom_name')

    @api.depends('type')
    def _compute_lhw_uom_name(self):
        self.lhw_uom_name = self.env.ref('uom.product_uom_cm').display_name

    @api.depends('product_variant_ids.length')
    def _compute_length(self):
        self._compute_template_field_from_variant_field('length')

    @api.depends('product_variant_ids.height')
    def _compute_height(self):
        self._compute_template_field_from_variant_field('height')

    @api.depends('product_variant_ids.width')
    def _compute_width(self):
        self._compute_template_field_from_variant_field('width')

    @api.depends('product_variant_ids.arms_code')
    def _compute_arms_code(self):
        self._compute_template_field_from_variant_field('arms_code')

    def _set_length(self):
        self._set_product_variant_field('length')

    def _set_height(self):
        self._set_product_variant_field('height')

    def _set_width(self):
        self._set_product_variant_field('width')

    def _set_arms_code(self):
        self._set_product_variant_field('arms_code')

    def _search_arms_code(self, operator, value):
        subquery = self.with_context(active_test=False)._search([
            ('product_variant_ids.arms_code', operator, value),
        ])
        return [('id', 'in', subquery)]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(ProductTemplate, self).name_search(name=name, args=args, operator=operator, limit=limit)
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
