# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit="res.partner"

    is_associate = fields.Boolean("Associate", tracking=True)

    associate_number = fields.Char(copy=False, tracking=True)
    group = fields.Boolean(tracking=True)
    company_group = fields.Many2one('company.group', tracking=True)
    company_group_number = fields.Integer(related="company_group.group_number", tracking=True)
    places = fields.Integer(tracking=True)
    rooms = fields.Integer(tracking=True)
    customer_type = fields.Selection([("active", "Active"),("inactive", "Inactive")], string="Client Type", tracking=True)
    registration_date = fields.Date(tracking=True)
    commercial_registration = fields.Many2one("hr.department", tracking=True)
    discharge_date = fields.Date(compute="_compute_discharge_date", tracking=True)
    discharge_reason = fields.Many2one('discharge.reason', tracking=True)

    terraces = fields.Boolean(tracking=True)
    terraces_type = fields.Selection(selection=[('a', 'A'), ('b', 'B')], tracking=True)
    file_number = fields.Text(tracking=True)
    start_date = fields.Date(tracking=True)
    grant_date = fields.Date(tracking=True)
    status = fields.Selection(selection=[('in_progress', 'In Progress'), ('granted', 'Granted')], string="Terraces Status", tracking=True)

    receive_press = fields.Boolean(tracking=True)
    receive_announcements = fields.Boolean(tracking=True)
    whatsapp_registration_date = fields.Date(tracking=True)
    whatsapp = fields.Boolean(tracking=True)
    whatsapp_phone = fields.Char(tracking=True)
    whatsapp_group = fields.Text(tracking=True)
    send_magazine = fields.Boolean(tracking=True)

    freelance_s_s_number = fields.Text(string="Freelance S.S. number", tracking=True)
    company_s_s_number = fields.Text(string="Company S.S. number", tracking=True)
    iae = fields.Text("IAE", tracking=True)
    cnae = fields.Text("CNAE", tracking=True)
    third_party_company = fields.Integer("Third-party company", tracking=True)
    freelance = fields.Integer(tracking=True)
    stopped_contract = fields.Boolean(tracking=True)
    stopped_contract_date = fields.Date(tracking=True)
    representative_id  = fields.Text(string="Representative ID", tracking=True)
    representative = fields.Text(tracking=True)

    quality_use_ids = fields.One2many(
        "partner.quality.use",
        "partner_id",
        string="Partner Quality Use",
    )
    associate_activity_ids = fields.One2many(
        "partner.activity",
        "partner_id",
        string="Associate Activities",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        spanish = self.env.ref("base.lang_es", raise_if_not_found=False)
        if spanish and spanish.active:
            res['lang'] = spanish.code
        return res

    @api.onchange('is_associate')
    def _onchange_is_associate(self):
        if not self.is_associate:
            spanish = self.env.ref("base.lang_es", raise_if_not_found=False)
            if spanish and spanish.active:
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
