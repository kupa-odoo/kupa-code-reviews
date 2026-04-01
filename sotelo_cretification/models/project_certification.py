# Part of Odoo. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup

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
            ("ready", "Certification Ready"),
            ("confirmed", "Confirmed")
        ],
        string="Status",
        readonly=True,
        copy=False,
        tracking=True,
        default="draft"
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        store=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        tracking=True
    )
    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice Address",
        compute="_compute_partner_related_fields",
        readonly=False
    )
    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Delivery Address",
        compute="_compute_partner_related_fields",
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
        compute="_compute_partner_related_fields",
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
        string="Total Accumulated",
        compute="_compute_accumulated_certification_total_amount",
        store=True,
        currency_field="currency_id"
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
    pending_total_amount = fields.Monetary(
        string=" Total Pending Amount",
        compute="_compute_pending_total_amount",
        store=True,
        currency_field="currency_id"
    )
    billable_status = fields.Selection(
        [
            ("billable", "Billable"),
            ("non_billable", "Non-Billable")
        ],
        string="Billing Type",
        default="non_billable",
        tracking=True
    )
    is_first_certification = fields.Boolean(
        string="Is First Certification",
        default=False
    )

    @api.depends("partner_id")
    def _compute_partner_related_fields(self):
        for certificate in self:
            partner = certificate.partner_id
            if partner:
                addresses = partner.address_get(["invoice", "delivery"])
                certificate.partner_invoice_id = addresses.get("invoice")
                certificate.partner_shipping_id = addresses.get("delivery")

                certificate = certificate.with_company(certificate.company_id)
                certificate.payment_term_id = partner.property_payment_term_id
            else:
                certificate.partner_invoice_id = False
                certificate.partner_shipping_id = False
                certificate.payment_term_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", self.env._("New")) == self.env._("New"):
                vals["name"] = self.env["ir.sequence"].with_company(vals.get('company_id')).next_by_code("project.certification") or self.env._("New")
        records = super().create(vals_list)
        for rec in records:
            if rec.project_id:
                rec.is_first_certification = len(rec.project_id.certification_ids) == 1
            else:
                rec.is_first_certification = False
        return records

    @api.onchange("project_id")
    def onchange_show_update_certification_line(self):
        self.show_update_certification_line = True

    @api.depends('certification_line_ids.accumulated_amount')
    def _compute_accumulated_certification_total_amount(self):
        for record in self:
            record.accumulated_certification_total_amount = sum(
                record.certification_line_ids.mapped("accumulated_amount")
            )

    @api.depends('certification_line_ids.pending_certi_amount')
    def _compute_pending_total_amount(self):
        for record in self:
            record.pending_total_amount = sum(
                record.certification_line_ids.mapped('pending_certi_amount')
            )

    def _get_previous_confirmed_certifications(self):
        self.ensure_one()
        if not self.project_id:
            return self.env["project.certification"]
        return self.project_id.certification_ids.filtered_domain([
            ("state", "=", "confirmed"),
            ("id", "<", self._origin.id),
        ])

    @api.depends(
        "project_id.certification_ids.state",
        "certification_line_ids.certification_amount",
        "project_id.certification_ids.total_to_invoice",
        "currency_id",
        "company_id",
        'project_id'
    )
    def _compute_certification_totals(self):
        for record in self:
            if record.state != 'confirmed':
                current_amount = record.accumulated_certification_total_amount or 0.0
                previous_confirmed_certs = record._get_previous_confirmed_certifications()
                previous_certifications = [
                    {
                        "name": cert.certificate_invoice_id.name or cert.name,
                        "amount": cert.total_to_invoice
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
                continue

            sale_orders = (
                record.project_id._fetch_sale_order_items(
                    {"project.task": [("is_closed", "=", False)]}
                )
                .sudo()
                .order_id.filtered_domain([("state", "=", "sale")])
            )
            record.partner_id = record.project_id.partner_id
            certificate_lines = [Command.clear()]
            for line in sale_orders.mapped("order_line"):
                if line.display_type == 'line_section':
                    certificate_lines.append(
                        Command.create({
                            "display_type": 'line_section',
                            "name": line.name,
                            "sale_id": line.order_id.id,
                            "sequence": line.sequence,
                        })
                    )
                    continue

                if line.display_type == 'line_note':
                    continue

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
            'name': self.env._('Invoice'),
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

    def _prepare_invoice_vals(self, previous_certs):
        project = self.project_id
        if not project.certification_product:
            raise UserError(
                self.env._("Please configure Certification Product on the project.")
            )
        if not project.invoice_deduction_product:
            raise UserError(
                self.env._("Please configure Invoice Deduction Product on the project.")
            )
        invoice_lines = self._prepare_invoice_lines(previous_certs)
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
        invoice_vals = self._prepare_invoice_vals(previous_certs)
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

    def action_mark_certfication_ready(self):
        for record in self:
            record.state = "ready"

    def write(self, vals):
        if 'billable_status' not in vals:
            return super().write(vals)
        old_status_map = {rec.id: rec.billable_status for rec in self}
        res = super().write(vals)
        for rec in self.filtered(lambda r: old_status_map.get(r.id) != r.billable_status):
            rec._post_billable_status_change(old_status_map[rec.id], rec.billable_status)
        return res

    def _post_billable_status_change(self, old_status, new_status):
        self.ensure_one()
        users = self.company_id.certification_user_ids
        if not users:
            return

        selection = dict(self._fields['billable_status'].selection)
        old_label = selection.get(old_status, old_status)
        new_label = selection.get(new_status, new_status)

        message = Markup(
            f"<p><strong>Billing Status Updated</strong><br/>"
            f"Certification <strong>{self.name}</strong>: "
            f"{old_label} → {new_label}<br/>"
            f"<strong>Updated by:</strong> {self.env.user.name}</p>"
        )
        self.message_post(
            body=message,
            partner_ids=users.mapped('partner_id').ids
        )
