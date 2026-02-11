# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit="hr.department"

    analytic_account = fields.Many2one('account.analytic.account', string="Analytic Account", domain="[('plan_id.is_department', '=', True)]")
