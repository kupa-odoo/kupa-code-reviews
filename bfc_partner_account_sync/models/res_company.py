# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    exclude_from_partner_sync = fields.Boolean(
        help="If true, partner level account sync will be not considered for this company."
    )
