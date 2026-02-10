# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit= 'account.payment'

    remaining_allocation_amount = fields.Float(
        string="Remaining Allocation Amount",
        help="Tracks the remaining amount that can be allocated to invoices/bills.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "remaining_allocation_amount" not in vals:
                vals["remaining_allocation_amount"] = vals.get("amount", 0.0)
        return super().create(vals_list)

    def action_open_allocate_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Allocate Payment'),
            'res_model': 'allocate.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'account.payment',
                'active_ids': self.ids
            }
        }
