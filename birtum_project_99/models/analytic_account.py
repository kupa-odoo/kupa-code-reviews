# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_99 = fields.Boolean("Is 99")

    plan_is_department = fields.Boolean(
        related="plan_id.is_department",
        store=True
    )
