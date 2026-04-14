# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import api, fields, models


class Investments(models.Model):
    _name = "investments.investment"
    _description = "Investments"

    project_id = fields.Many2one("project.project")
    customer = fields.Many2one(related="project_id.partner_id", store=True)
    label = fields.Char()
    date = fields.Date(default=lambda self: fields.Date.today() + timedelta(days=30))
    added_to_so = fields.Boolean()
    company_id = fields.Many2one(related='project_id.company_id')
    currency_id = fields.Many2one(related='company_id.currency_id')
    investment = fields.Monetary(currency_field="currency_id")
    amount_to_invoice = fields.Monetary(
        currency_field="currency_id",
        readonly=True
    )
    product_id = fields.Many2one(
        "product.product",
        domain=[('type', '=', 'service')],
        default= lambda self: self._get_default_product()
    )
    has_investment = fields.Boolean(default=False)

    def _get_default_product(self):
        param = self.env['ir.config_parameter'].sudo().get_param(
            'nalios_retirement_timeline.investment_product'
        )
        return int(param) if param else False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._allocate_investment()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'investment' in vals:
            for rec in self:
                rec._allocate_investment()
        return res

    def _allocate_investment(self):
        for rec in self:
            amount_to_invoice = 0.0
            investment_remaining = rec.investment or 0.0
            if not investment_remaining:
                rec.amount_to_invoice = 0.0
                continue

            rec.has_investment = True
            lines = rec.project_id.retirement_timeline_ids.filtered(
                lambda l: l.remaining_to_invest > 0
            ).sorted(key=lambda l: l.ceiling)

            for line in lines:
                if investment_remaining <= 0:
                    break
                allocation_amount = min(investment_remaining, line.remaining_to_invest)
                amount_to_invoice += allocation_amount * (line.pct_invest)
                line.write({
                    'remaining_to_invest': line.remaining_to_invest - allocation_amount,
                    'has_timeline_used' : True
                })
                investment_remaining -= allocation_amount
            rec.amount_to_invoice = amount_to_invoice

    @api.model
    def _cron_add_investments_to_sale_order(self):
        today = fields.Date.today()
        investments = self.search([
            ('date', '<=', today),
            ('added_to_so', '=', False)
        ])
        for inv in investments.filtered(lambda inve: inve.project_id.reinvoiced_sale_order_id):
            self.env["sale.order.line"].create({
                'order_id': inv.project_id.reinvoiced_sale_order_id.id,
                'name': inv.label or 'Investment',
                'product_id': inv.product_id.id,
                'product_uom_qty': 1,
                'price_unit': inv.amount_to_invoice,
            })
            inv.added_to_so = True
