# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class BudgetAnalytic(models.Model):
    _inherit = 'budget.analytic'

    is_approved  = fields.Boolean("Is Approved", readonly=True, copy=False)
    is_approval_requested = fields.Boolean("Is Approval Requested", readonly=True, copy=False)

    def action_request_approval(self):
        users = self.env.ref('BFC_analytic_budget.group_analytic_budget_releaser').user_ids
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        partner_model_id = self.env['ir.model']._get_id('res.partner')
        for user in users:
            self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'user_id': user.id,
                'res_model_id': partner_model_id,
                'res_id': user.partner_id.id,
                'date_deadline': fields.Date.today(),
                'summary': _('Budget Approval Requested'),
                'note': _(
                    'A budget %(budget)s requires your approval.<br/>%(link)s'
                ) % {
                    'budget': self.name,
                    'link': self._get_html_link(_('Click here to review the budget')),
                },
            })
        self.is_approval_requested = True

    def action_approve_budget(self):
        self.action_budget_confirm()
        self.is_approved = True

    def action_budget_draft(self):
        super().action_budget_draft()
        self.is_approval_requested = False
        self.is_approved = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if self.env.context.get('project_update'):
                if self.env.user.has_group('BFC_analytic_budget.group_analytic_budget_releaser'):
                    record.state = 'confirmed'
                    record.is_approved=True
                else:
                    record.state = 'draft'
        return records
