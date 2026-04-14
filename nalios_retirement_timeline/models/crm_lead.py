# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_ids = fields.One2many(
        'project.project',
        compute='_compute_project_ids',
        string="Projects"
    )
    folder_ids = fields.One2many(
        'documents.document',
        compute='_compute_folder_ids',
        string="Workspaces"
    )
    document_count = fields.Integer(compute='_compute_counts')
    tasks_count = fields.Integer(compute='_compute_counts')
    investment_count = fields.Integer(compute='_compute_counts')

    @api.depends('order_ids')
    def _compute_project_ids(self):
        for lead in self:
            lead.project_ids = lead.order_ids.mapped('project_ids')

    @api.depends('project_ids', 'project_ids.documents_folder_id')
    def _compute_folder_ids(self):
        for lead in self:
            lead.folder_ids = lead.project_ids.mapped('documents_folder_id')

    @api.depends(
        'project_ids',
        'project_ids.task_ids',
        'project_ids.investment_ids',
        'project_ids.documents_folder_id'
    )
    def _compute_counts(self):
        for lead in self:
            projects = lead.project_ids
            if not projects:
                lead.tasks_count = 0
                lead.investment_count = 0
                lead.document_count = 0
                continue
            lead.tasks_count = sum(len(p.task_ids) for p in projects)
            lead.investment_count = sum(len(p.investment_ids) for p in projects)
            lead.document_count = sum(p.documents_folder_id.document_count for p in projects)

    def action_view_documents(self):
        self.ensure_one()
        if not self.folder_ids:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'documents.document',
            'view_mode': 'kanban,list,form',
            'domain': [('folder_id', '=', self.folder_ids.ids)],
            'context': {
                'default_folder_id': self.folder_ids[:1].id,
            }
        }

    def action_view_tasks(self):
        self.ensure_one()
        if not self.project_ids:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'kanban,list,form',
            'domain': [('project_id', 'in', self.project_ids.ids)],
        }

    def action_view_investments(self):
        self.ensure_one()
        if not self.project_ids:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Investments',
            'res_model': 'investments.investment',
            'view_mode': 'list',
            'domain': [('project_id', 'in', self.project_ids.ids)],
        }
