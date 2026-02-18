# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectCertificationLine(models.Model):
    _name = "project.certification.line"
    _description = "Project Certification Line"
    _check_certification_percentage_positive = models.Constraint(
        "CHECK(certification_percentage >= 0)",
        "Certification Percentage must be Positive.",
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='certification_id.currency_id',
        depends=['certification_id.currency_id'],
        store=True,
        readonly=True
    )
    certification_id = fields.Many2one(
        'project.certification',
        string="Certification",
        required=True,
        ondelete='cascade'
    )
    sale_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    sale_line_id = fields.Many2one('sale.order.line', string="Sale Order Line", readonly=True)
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    product_uom_qty = fields.Float(string="Quantity", readonly=True)
    price_unit = fields.Float(string="Unit Price", readonly=True)
    discount = fields.Float(string="Discount (%)",readonly=True)
    net_unit_price = fields.Float(string="Net Unit Price", compute="_compute_net_unit_price", readonly=True)
    price_subtotal = fields.Monetary(string="Line Total", currency_field='currency_id', readonly=True)

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
    certification_percentage = fields.Float("Certidcation Percentage")

    certification_uds = fields.Float("Certification Uds", compute="_compute_all_certification_values")
    certification_amount = fields.Monetary("Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id')

    accumulated_percentage =  fields.Float("Accumulated Percentage", compute="_compute_all_certification_values")
    accumulated_uds = fields.Float("Accumulated Uds", compute="_compute_all_certification_values")
    accumulated_amount = fields.Monetary("Accumulated Amount", compute="_compute_all_certification_values", currency_field='currency_id')

    pending_ceri_percentage = fields.Float("Pending Certification Percentage", compute="_compute_all_certification_values")
    pending_certi_uds = fields.Float("Pending Certification uds", compute="_compute_all_certification_values")
    pending_certi_amount = fields.Monetary("Pending Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id')

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
        string="Previous Work Status"
    )
    prev_certification_percentage = fields.Float("Previous Certidcation Percentage")

    prev_certification_uds = fields.Float("Previous Certification Uds", compute="_compute_all_certification_values")
    prev_certification_amount = fields.Monetary("Previous Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id')

    prev_accumulated_uds = fields.Float("Previous Accumulated Uds", compute="_compute_all_certification_values")
    prev_accumulated_percentage =  fields.Float("Previous Accumulated Percentage", compute="_compute_all_certification_values")
    prev_accumulated_amount = fields.Monetary("Previous Accumulated Amount", compute="_compute_all_certification_values", currency_field='currency_id')

    prev_pending_ceri_percentage = fields.Float("Previous Pending Certification Percentage", compute="_compute_all_certification_values")
    prev_pending_certi_uds = fields.Float("Previous Pending Certification uds", compute="_compute_all_certification_values")
    prev_pending_certi_amount = fields.Monetary("Previous Pending Certification Amount", compute="_compute_all_certification_values", currency_field='currency_id')

    @api.depends('price_unit', 'discount')
    def _compute_net_unit_price(self):
        for record in self:
            record.net_unit_price = record.price_unit *  (1 - record.discount / 100)

    @api.depends(
        'certification_percentage',
        'prev_certification_percentage',
        'product_uom_qty',
        'price_subtotal'
    )
    def _compute_all_certification_values(self):
        for record in self:
            qty = record.product_uom_qty or 0.0
            subtotal = record.price_subtotal or 0.0

            cert_pct = record.certification_percentage or 0.0
            prev_cert_pct = record.prev_certification_percentage or 0.0

            record.prev_certification_uds = prev_cert_pct * qty
            record.prev_certification_amount = prev_cert_pct * subtotal

            record.prev_accumulated_percentage = prev_cert_pct
            record.prev_accumulated_uds = prev_cert_pct * qty
            record.prev_accumulated_amount = prev_cert_pct * subtotal

            record.prev_pending_ceri_percentage = 1 - prev_cert_pct
            record.prev_pending_certi_uds = qty - record.prev_accumulated_uds
            record.prev_pending_certi_amount = subtotal - record.prev_accumulated_amount

            record.certification_uds = cert_pct * qty
            record.certification_amount = cert_pct * subtotal

            accumulated_pct = prev_cert_pct + cert_pct

            record.accumulated_percentage = accumulated_pct
            record.accumulated_uds = accumulated_pct * qty
            record.accumulated_amount = accumulated_pct * subtotal

            record.pending_ceri_percentage = 1 - accumulated_pct
            record.pending_certi_uds = qty - record.accumulated_uds
            record.pending_certi_amount = subtotal - record.accumulated_amount
