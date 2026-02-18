# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models
from odoo.exceptions import UserError


class ProjectCertification(models.Model):
    _name = "project.certification"
    _description = "Project Certification"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Certiifcation Reference",
        required=True,
        copy=False,
        index="trigram",
        default=lambda self: self.env._("New")
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed")
        ],
        string="Status",
        readonly=True,
        copy=False,
        tracking=True,
        default="draft"
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_currency_id",
        store=True,
        ondelete="restrict"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        tracking=1
    )
    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice Address",
        compute="_compute_partner_invoice_id",
        readonly=False
    )
    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Delivery Address",
        compute="_compute_partner_shipping_id",
        readonly=False
    )
    date_certification = fields.Datetime(
        string="Certification Date",
        required=True,
        copy=False,
        help="Creation date of draft Certification.",
        default=fields.Datetime.now
    )
    project_id = fields.Many2one(
        "project.project",
        domain=[("allow_billable", "=", True), ("is_template", "=", False)],
        copy=False
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Payment Terms",
        compute="_compute_payment_term_id",
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    certification_line_ids = fields.One2many(
        "project.certification.line",
        "certification_id",
        string="Certification Lines"
    )
    show_update_certification_line = fields.Boolean()
    accumulated_certification_total_amount = fields.Monetary(
        compute="_compute_accumulated_certification_total_amount",
        store=True
    )
    certification_totals = fields.Json(
        compute="_compute_certification_totals",
        exportable=False,
        store=True
    )
    certificate_invoice_id = fields.Many2one("account.move")
    note = fields.Html(
        string="Terms and conditions"
    )
    total_to_invoice = fields.Monetary(
        string="Total To Invoice Amount",
        default="0.0",
        currency_field="currency_id"
    )

    @api.depends("partner_id")
    def _compute_partner_invoice_id(self):
        for certificate in self:
            certificate.partner_invoice_id = (
                certificate.partner_id.address_get(["invoice"])["invoice"]
                if certificate.partner_id
                else False
            )

    @api.depends("partner_id")
    def _compute_partner_shipping_id(self):
        for certificate in self:
            certificate.partner_shipping_id = (
                certificate.partner_id.address_get(["delivery"])["delivery"]
                if certificate.partner_id
                else False
            )

    @api.depends("company_id")
    def _compute_currency_id(self):
        for certificate in self:
            certificate.currency_id = certificate.company_id.currency_id

    @api.depends("partner_id")
    def _compute_payment_term_id(self):
        for certificate in self:
            certificate = certificate.with_company(certificate.company_id)
            certificate.payment_term_id = certificate.partner_id.property_payment_term_id

    def create(self, vals):
        if vals.get("name", self.env._("New")) == self.env._("New"):
            vals["name"] = self.env["ir.sequence"].with_company(
                vals.get("company_id")
            ).next_by_code("project.certification") or self.env._("New")
        return super().create(vals)

    @api.onchange("project_id")
    def _onchange_show_update_certification_line(self):
        self.show_update_certification_line = True

    @api.depends('certification_line_ids.accumulated_amount')
    def _compute_accumulated_certification_total_amount(self):
        for record in self:
            record.accumulated_certification_total_amount = sum(
                record.certification_line_ids.mapped("accumulated_amount")
            )

    def _get_previous_confirmed_certifications(self):
        self.ensure_one()
        if not self.project_id:
            return self.env["project.certification"]
        return self.env["project.certification"].search(
            [
                ("project_id", "=", self.project_id.id),
                ("state", "=", "confirmed"),
                ("id", "!=", self.id)
            ]
        )

    @api.depends(
        "certification_line_ids.certification_amount",
        "currency_id",
        "company_id"
    )
    def _compute_certification_totals(self):
        for record in self:
            if record.state != 'confirmed':
                current_amount = record.accumulated_certification_total_amount or 0.0
                previous_confirmed_certs = self._get_previous_confirmed_certifications()
                previous_certifications = [
                    {
                        "name": cert.certificate_invoice_id.name or cert.name,
                        "amount": cert.total_to_invoice,
                    }
                    for cert in previous_confirmed_certs
                ]
                previous_amount = sum(previous_confirmed_certs.mapped("total_to_invoice"))
                record.certification_totals = {
                    "current_certification_amount": current_amount,
                    "previous_certifications": previous_certifications,
                    "total_net_amount": current_amount - previous_amount
                }

    def action_update_certification_line(self):
        for record in self:
            if not record.project_id:
                record.certification_line_ids = [Command.clear()]
                return
            sale_orders = (
                record.project_id._fetch_sale_order_items(
                    {"project.task": [("is_closed", "=", False)]}
                )
                .sudo()
                .order_id.filtered_domain([("state", "=", "sale")])
            )
            record.partner_id = record.project_id.partner_id
            certificate_lines = [Command.clear()]
            sale_lines = sale_orders.mapped("order_line")
            for line in sale_lines:
                certificate_lines.append(
                    Command.create(
                        {
                            "sale_id": line.order_id.id,
                            "sale_line_id": line.id,
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.product_uom_qty,
                            "price_unit": line.price_unit,
                            "discount": line.discount,
                            "price_subtotal": line.price_subtotal
                        }
                    )
                )
            record.certification_line_ids = certificate_lines
            record.show_update_certification_line = False

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.certificate_invoice_id.id,
            'target': 'current'
        }

    def _prepare_invoice_lines(self, previous_confirmed_certs):
        project = self.project_id
        invoice_lines = []

        invoice_lines.append(
            Command.create(
                {
                    "product_id": project.certification_product.id,
                    "name": project.certification_product.display_name,
                    "quantity": 1,
                    "price_unit": self.accumulated_certification_total_amount
                }
            )
        )
        for cert in previous_confirmed_certs:
            invoice_lines.append(
                Command.create(
                    {
                        "product_id": project.invoice_deduction_product.id,
                        "name": self.env._("Deduction - %s") % cert.name,
                        "quantity": -1,
                        "price_unit": cert.total_to_invoice
                    }
                )
            )
        return invoice_lines

    def _prepare_invoice_vals(self):
        project = self.project_id
        if not project.certification_product:
            raise UserError(
                self.env._("Please configure Certification Product on the project.")
            )
        if not project.invoice_deduction_product:
            raise UserError(
                self.env._("Please configure Invoice Deduction Product on the project.")
            )
        previous_confirmed_certs = self.env["project.certification"].search(
            [
                ("project_id", "=", project.id),
                ("state", "=", "confirmed")
            ]
        )
        invoice_lines = self._prepare_invoice_lines(previous_confirmed_certs)
        return {
            "move_type": "out_invoice",
            "partner_id": self.partner_invoice_id.id or self.partner_id.id,
            "invoice_origin": self.name,
            "invoice_line_ids": invoice_lines,
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
            "invoice_payment_term_id": self.payment_term_id.id,
            "partner_shipping_id": self.partner_shipping_id.id or self.partner_id.id,
            'certfication_id': self.id
        }

    def action_create_invoice(self):
        self.ensure_one()
        previous_certs = self._get_previous_confirmed_certifications()
        previous_amount = sum(
            previous_certs.mapped("total_to_invoice")
        )
        invoice_vals = self._prepare_invoice_vals()
        invoice = self.env["account.move"].create(invoice_vals)
        self.write({
            "total_to_invoice": self.accumulated_certification_total_amount - previous_amount,
            "certificate_invoice_id": invoice.id,
            "state": "confirmed"
        })
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Customer Invoice"),
            "res_model": "account.move",
            "res_id": invoice.id,
            "view_mode": "form"
        }
