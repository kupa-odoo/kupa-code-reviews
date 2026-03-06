# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Override field
    owner_name = fields.Char(
        compute="_compute_owner_name",
        store=True,
        readonly=False
    )

    @api.depends("partner_id")
    def _compute_owner_name(self):
        for rec in self:
            address = rec.partner_id.contact_address_ids
            rec.owner_name = address.owner_reference if address else False
