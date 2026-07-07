# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AnalyticCostGroup(models.Model):
    _name = 'analytic.cost.group'
    _description = 'Analytic Cost Group'
    _order = 'code'
    _rec_name = 'code'

    code = fields.Char(string='Cost Group Code', required=True)
    name_de = fields.Char(string='Description DE', required=True)
    name_en = fields.Char(string='Description EN')

    @api.model
    def _compute_display_name(self):
        super()._compute_display_name()
        for rec in self:
            rec.display_name = f"{rec.code} {rec.name_de}"
