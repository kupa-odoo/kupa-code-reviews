# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError, MissingError


class AllocatePayment(models.TransientModel):
    _name = "allocate.payment"
    _description = "Allocate Payment"

    payment_ids = fields.Many2many('account.payment', string="Selected Payments")
    partner_name = fields.Many2one('res.partner', string="Partner", readonly=True)
    payment_amount = fields.Float(string="Payment Amount", readonly=True)
    avaliable_amount = fields.Float(string="Avaliable Amount", compute="_compute_avaliable_amount")
    invoice_ids = fields.One2many(
        'allocate.payment.line',
        'payment_line_id',
        string='Invoice/Bills',
    )

    @api.depends('invoice_ids.amount')
    def _compute_avaliable_amount(self):
        for record in self:
            total_allocated = sum(line.amount for line in record.invoice_ids)
            if((record.payment_amount - total_allocated) < 0) :
                raise ValidationError("Allocated amount exceeds available payment amount.")
            record.avaliable_amount = record.payment_amount - total_allocated

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        payments = self.env['account.payment'].browse(self._context.get('active_ids', []))
        payment_type = None
        total_payment_amount = 0
        for payment in payments:
            if not payment.partner_id:
                raise MissingError("Select a partner in the payment before allocation.")
            if payment.state == 'draft':
                raise UserError("Selected Payment does not belong to draft state")
            if payment.remaining_allocation_amount <= 0:
                raise UserError("Please select only payments with an amount greater than zero.")
            if payment.invoice_ids or payment.reconciled_invoice_ids:
                raise ValidationError(
                    f"Payment {payment.name} is already linked to an invoice. "
                    "You cannot allocate it again."
                )

            if payment_type is None:
                payment_type = payment.payment_type
            elif payment.payment_type != payment_type:
                raise UserError("All selected payments must have the same payment type")
            total_payment_amount += payment.remaining_allocation_amount

        partners = payments.mapped('partner_id')

        if len(partners) != 1:
            raise UserError("All selected payments must belong to the same partner.")
        partner = partners[0]
        payment_type = payments[0].payment_type
        company_id = payments[0].company_id
        moves = self._prepare_wizard_data(partner, payment_type, company_id)
        res.update({
            'partner_name' : partner.id,
            'payment_amount': total_payment_amount,
            'avaliable_amount': total_payment_amount,
            'invoice_ids': moves,
            'payment_ids': [(6, 0, payments.ids)],
        })
        return res

    def _prepare_wizard_data(self, partner, payment_type, company):
        domain = [
            ('partner_id', '=', partner.id),
            ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
            ('state', '=', 'posted'),
            ('company_id', '=', company.id)
        ]
        if payment_type == "inbound":
            domain.append(("move_type", '=', 'out_invoice'))
        else:
            domain.append(("move_type", '=', 'in_invoice'))

        invoices = self.env['account.move'].search(domain)
        lines = []
        for invoice in invoices:
            lines.append((0, 0, {
                'move_id': invoice.id,
                'total_amount': invoice.amount_residual,
                'amount': 0.0,
            }))

        return lines

    def allocate_payment(self):
        for line in filter(lambda line: line.amount > 0, self.invoice_ids):
            invoice = line.move_id
            allocation_amount = line.amount

            for payment in self.payment_ids.filtered(lambda payment: payment.remaining_allocation_amount > 0):
                payment_to_apply = min(payment.remaining_allocation_amount, allocation_amount)
                if payment_to_apply <= 0:
                    continue

                self._create_register_payment(invoice, payment, payment_to_apply)
                payment.remaining_allocation_amount -= payment_to_apply
                allocation_amount -= payment_to_apply

    def _create_register_payment(self, invoice, payment, amount_to_apply):
        register_vals = {
            'partner_id': self.partner_name.id,
            'amount': amount_to_apply,
            'payment_date': fields.Date.today(),
            'journal_id': payment.journal_id.id,
        }
        payment=self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=[invoice.id]
        ).create(register_vals)._create_payments()
        payment.state='paid'
