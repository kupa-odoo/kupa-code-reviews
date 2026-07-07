# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    certification_user_ids = fields.Many2many(
        "res.users",
        string="Allowed Certification Users"
    )
