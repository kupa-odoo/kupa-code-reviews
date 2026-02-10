# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AllocatePaymentLine(models.TransientModel):
    _name = 'allocate.payment.line'
    _description = 'Allocate Payment Line'
    _sql_constraints = [
        (
            'check_positive_amount',
            'CHECK(amount >= 0)',
            'The amount must be a positive value.'
        )
    ]
    payment_line_id = fields.Many2one(
        'allocate.payment',
        string='Wizard Reference',
        required=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string="Invoice/Bill",
        required=True,
    )
    total_amount = fields.Float(string="Amount Due")
    amount = fields.Float(string='Amount', required=True)

    @api.onchange('amount')
    def _onchange_amount(self):
        for record in self:
            if record.amount > record.total_amount:
                raise ValidationError(f"Cannot allocate {record.amount} to invoice {record.move_id.name} which only has {record.total_amount} due.")
