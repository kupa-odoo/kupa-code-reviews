# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectCertificationLine(models.Model):
    _name = "project.certification.line"
    _description = "Project Certification Line"
    _check_certification_percentage_valid = models.Constraint(
        'check(certification_percentage >= 0 and certification_percentage <= 1)',
        "Certification Percentage must be between 0 to 100."
    )
    _check_accumulated_percentage_valid = models.Constraint(
        'check(accumulated_percentage >= 0 and accumulated_percentage <= 1)',
        "Accumulated Percentage must be between 0 to 100."
    )

    currency_id = fields.Many2one(
        related='certification_id.currency_id',
        store=True
    )
    certification_id = fields.Many2one(
        'project.certification',
        string="Certification",
        required=True,
        ondelete='cascade'
    )
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section")
        ],
        default=False)
    name = fields.Char("Description")
    sequence = fields.Integer()
    sale_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    sale_line_id = fields.Many2one('sale.order.line', string="Sale Order Line", readonly=True)
    product_id = fields.Many2one('product.product', string="Product")
    product_uom_qty = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price")
    discount = fields.Float(string="Discount (%)")
    net_unit_price = fields.Float(string="Net Unit Price", compute="_compute_net_unit_price")
    price_subtotal = fields.Monetary(string="Line Total", currency_field='currency_id', compute="_compute_price_subtotal", store=True)

    work_status = fields.Selection(
        [
            ('advance_accepted', 'Advance accepted'),
            ('accepted', 'Accepted'),
            ('sum_carp', 'Sum. Carp.'),
            ('sum_glass', 'Sum. Glass'),
            ('glass_installation', 'Glass Installation'),
            ('falta_remate', 'Falta remate'),
            ('supply', 'Supply'),
            ('finished', 'Finished')
        ],
        string="Work Status"
    )

    certification_percentage = fields.Float(
        compute="_compute_certification_percentage",
        inverse="_inverse_certification_percentage",
        store=True
    )

    certification_uds = fields.Float(
        compute="_compute_certification_uds",
        inverse="_inverse_certification_uds",
        store=True
    )
    certification_amount = fields.Monetary(compute="_compute_all_certification_values", currency_field='currency_id', store=True)

    accumulated_percentage =  fields.Float(compute="_compute_all_certification_values", store=True)
    accumulated_uds = fields.Float(compute="_compute_all_certification_values", store=True)
    accumulated_amount = fields.Monetary(compute="_compute_all_certification_values", currency_field='currency_id', store=True)

    pending_ceri_percentage = fields.Float("Pending Certification Percentage", compute="_compute_all_certification_values", store=True)
    pending_certi_uds = fields.Float("Pending Certification uds", compute="_compute_all_certification_values", store=True)
    pending_certi_amount = fields.Monetary("Pending Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id', store=True)

    prev_work_status = fields.Selection(
        [
            ('advance_accepted', 'Advance accepted'),
            ('accepted', 'Accepted'),
            ('sum_carp', 'Sum. Carp.'),
            ('sum_glass', 'Sum. Glass'),
            ('glass_installation', 'Glass Installation'),
            ('falta_remate', 'Falta remate'),
            ('supply', 'Supply'),
            ('finished', 'Finished')
        ],
        string="Previous Work Status",
        compute="_compute_prev_work_status_percentage"
    )
    prev_certification_percentage = fields.Float("Previous Certification Percentage", compute="_compute_prev_work_status_percentage")

    prev_certification_uds = fields.Float("Previous Certification Uds", compute="_compute_all_certification_values", store=True)
    prev_certification_amount = fields.Monetary("Previous Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id', store=True)

    prev_accumulated_uds = fields.Float("Previous Accumulated Uds", compute="_compute_all_certification_values", store=True)
    prev_accumulated_percentage =  fields.Float("Previous Accumulated Percentage", compute="_compute_prev_accumulated_percentage", readonly=False, store=True)
    is_prev_accumulated_manual = fields.Boolean(default=False)
    is_prev_accumulated_changed = fields.Boolean(default=False)
    prev_accumulated_amount = fields.Monetary("Previous Accumulated Amount", compute="_compute_all_certification_values", currency_field='currency_id', store=True)

    prev_pending_certi_percentage = fields.Float("Previous Pending Certification Percentage", compute="_compute_all_certification_values", store=True)
    prev_pending_certi_uds = fields.Float("Previous Pending Certification uds", compute="_compute_all_certification_values", store=True)
    prev_pending_certi_amount = fields.Monetary("Previous Pending Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id', store=True)

    @api.depends('price_unit', 'discount')
    def _compute_net_unit_price(self):
        for record in self:
            record.net_unit_price = record.price_unit *  (1 - record.discount / 100)

    @api.depends('product_uom_qty', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for rec in self:
            net_price = rec.price_unit * (1 - (rec.discount or 0.0) / 100)
            rec.price_subtotal = rec.product_uom_qty * net_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if not rec.product_id:
                continue

            rec.product_uom_qty = 1.0
            rec.price_unit = rec.product_id.lst_price
            rec.discount = 0.0

    @api.depends(
        "certification_id",
        "sale_line_id",
        "certification_id.project_id.certification_ids.state"
    )
    def _compute_prev_work_status_percentage(self):
        for record in self:
            record.prev_work_status = False
            record.prev_certification_percentage = 0.0

            cert = record.certification_id
            previous_certs = cert.project_id.certification_ids.filtered(
                lambda c: (
                    c.id < cert.id
                )
            ).sorted(key=lambda c: c.id, reverse=True)

            if previous_certs:
                prev_line = previous_certs[0].certification_line_ids.filtered(
                    lambda l: l.sale_line_id.id == record.sale_line_id.id
                )
                if prev_line:
                    record.prev_work_status = prev_line.work_status
                    record.prev_certification_percentage = prev_line.certification_percentage or 0.0

    @api.depends('product_uom_qty', 'certification_percentage')
    def _compute_certification_uds(self):
        for record in self:
            record.certification_uds = (record.certification_percentage) * record.product_uom_qty

    @api.depends('product_uom_qty', 'certification_uds')
    def _compute_certification_percentage(self):
        for record in self:
            record.certification_percentage = (record.certification_uds / record.product_uom_qty) if record.product_uom_qty else 0

    def _inverse_certification_percentage(self):
        for record in self:
            record.certification_uds = (record.certification_percentage) * record.product_uom_qty

    def _inverse_certification_uds(self):
        for record in self:
            record.certification_percentage = (record.certification_uds / record.product_uom_qty) if record.product_uom_qty else 0

    @api.depends(
        'prev_certification_percentage',
        'is_prev_accumulated_changed'
    )
    def _compute_prev_accumulated_percentage(self):
        for rec in self:
            if rec.is_prev_accumulated_manual and rec._origin:
                continue
            rec.prev_accumulated_percentage = rec.prev_certification_percentage or 0.0

    @api.depends(
        'certification_percentage',
        'product_uom_qty',
        'price_subtotal',
        'is_prev_accumulated_changed'
    )
    def _compute_all_certification_values(self):
        for record in self:
            qty = record.product_uom_qty or 0.0
            subtotal = record.price_subtotal or 0.0

            cert_pct = record.certification_percentage or 0.0
            prev_cert_pct = record.prev_certification_percentage or 0.0
            prev_accumulated_pct = record.prev_accumulated_percentage

            accumulated_pct = prev_accumulated_pct + cert_pct

            prev_accumulated_uds = prev_accumulated_pct * qty
            prev_accumulated_amount = prev_accumulated_pct * subtotal

            accumulated_uds = accumulated_pct * qty
            accumulated_amount = accumulated_pct * subtotal

            record.update({
                'prev_certification_uds': prev_cert_pct * qty,
                'prev_certification_amount': prev_cert_pct * subtotal,

                'prev_accumulated_uds': prev_accumulated_uds,
                'prev_accumulated_amount': prev_accumulated_amount,

                'prev_pending_certi_percentage': 1 - prev_accumulated_pct,
                'prev_pending_certi_uds': qty - prev_accumulated_uds,
                'prev_pending_certi_amount': subtotal - prev_accumulated_amount,

                'certification_amount': cert_pct * subtotal,

                'accumulated_percentage': accumulated_pct,
                'accumulated_uds': accumulated_uds,
                'accumulated_amount': accumulated_amount,

                'pending_ceri_percentage': 1 - accumulated_pct,
                'pending_certi_uds': qty - accumulated_uds,
                'pending_certi_amount': subtotal - accumulated_amount
            })
