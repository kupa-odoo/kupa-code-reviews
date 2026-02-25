# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_associate = fields.Boolean("Associate")

    associate_number = fields.Char(readonly=True, copy=False, tracking=True)
    group = fields.Boolean(tracking=True)
    company_group = fields.Many2one("company.group", tracking=True)
    company_group_number = fields.Integer(compute="_compute_company_group_number", tracking=True)
    places = fields.Integer(tracking=True)
    rooms = fields.Integer(tracking=True)
    extra_beds = fields.Integer(tracking=True)
    customer_type = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")], string="Client Type", tracking=True
    )
    registration_date = fields.Date(tracking=True)
    commercial_registration = fields.Many2one("hr.department", tracking=True)
    discharge_date = fields.Date(compute="_compute_discharge_date", tracking=True)
    discharge_reason = fields.Many2one("discharge.reason", tracking=True)

    terraces = fields.Boolean()
    terraces_type = fields.Selection(selection=[("a", "A"), ("b", "B")])
    file_number = fields.Text()
    start_date = fields.Date()
    grant_date = fields.Date()
    status = fields.Selection(
        selection=[("in_progress", "In Progress"), ("granted", "Granted")], string="Terraces Status"
    )

    receive_press = fields.Boolean()
    receive_announcements = fields.Boolean()
    whatsapp_registration_date = fields.Date()
    whatsapp = fields.Boolean()
    whatsapp_group = fields.Text()
    send_magazine = fields.Boolean()

    freelance_s_s_number = fields.Text(string="Freelance S.S. number")
    company_s_s_number = fields.Text(string="Company S.S. number")
    iae = fields.Text("IAE")
    cnae = fields.Text("CNAE")
    third_party_company = fields.Integer("Third-party company")
    freelance = fields.Integer()
    stopped_contract = fields.Boolean()
    stopped_contract_date = fields.Date()

    quality_use_ids = fields.One2many(
        "partner.quality.use",
        "partner_id",
        string="Partner Quality Use",
    )
    associate_activity_ids = fields.One2many("partner.activity", "partner_id", string="Associate Activities")

    @api.depends("company_group")
    def _compute_company_group_number(self):
        for record in self:
            record.company_group_number = record.company_group.group_number

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        spanish = self.env["res.lang"].search([("code", "=", "es_ES"), ("active", "=", True)], limit=1)
        if spanish:
            res["lang"] = spanish.code
        return res

    @api.onchange("is_associate")
    def _onchange_is_associate(self):
        if not self.is_associate:
            spanish = self.env["res.lang"].search([("code", "=", "es_ES"), ("active", "=", True)], limit=1)
            if spanish:
                self.lang = spanish.code

    def action_generate_associate_number(self):
        for partner in self:
            if partner.associate_number:
                raise UserError("Associate Number already generated.")
            partner.associate_number = self.env["ir.sequence"].next_by_code("res.partner.associate")
            partner.registration_date = fields.Date.today()

    @api.depends("customer_type")
    def _compute_discharge_date(self):
        for record in self:
            record.discharge_date = fields.Date.today() if record.customer_type == "inactive" else False
