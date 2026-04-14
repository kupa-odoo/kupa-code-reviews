# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class RetirementTimeline(models.Model):
    _name = 'retirement.timeline'
    _description = "Retirement Timeline"
    _order = 'ceiling asc'

    project_id = fields.Many2one('project.project')
    label = fields.Char()
    company_id = fields.Many2one(related='project_id.company_id')
    currency_id = fields.Many2one(related='company_id.currency_id')
    ceiling = fields.Monetary(currency_field='currency_id')
    pct_invest = fields.Float(
        string="% Invest."
    )
    remaining_to_invest = fields.Monetary(
        currency_field='currency_id',
        compute="_compute_remaining_to_invest",
        readonly=False,
        store=True
    )
    has_timeline_used = fields.Boolean()

    @api.depends('ceiling')
    def _compute_remaining_to_invest(self):
        for rec in self:
            if not rec.ceiling:
                rec.remaining_to_invest = 0.0
            lines = rec.project_id.retirement_timeline_ids.filtered(
                lambda l: l != rec and l.ceiling < rec.ceiling
            ).sorted(key=lambda l: l.ceiling)
            if lines:
                rec.remaining_to_invest = rec.ceiling - lines[-1].ceiling
            else:
                rec.remaining_to_invest = rec.ceiling
