from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        portal_users = users.filtered(lambda user: user._is_portal())
        portal_users._create_portal_documents()
        return users

    def write(self, vals):
        users_before = {user.id: user._is_portal() for user in self}
        res = super().write(vals)
        portal_users = self.filtered(
            lambda user: not users_before.get(user.id) and user._is_portal()
        )
        portal_users._create_portal_documents()
        return res

    def _create_portal_documents(self):
        root_id = self.env['ir.config_parameter'].sudo().get_param('nalios_retirement_timeline.default_portal_folder')
        if not root_id:
            return
        root = self.env['documents.document'].browse(int(root_id))
        for rec in self:
            rec._copy_document_tree(root, parent=None)

    def _copy_document_tree(self, record, parent=None):
        vals = {
            'name': f"{record.name} - {self.partner_id.name}",
            'type': record.type,
            'folder_id': parent.id if parent else False,
            'partner_id': self.partner_id.id,
            'owner_id': self.env.user.id if parent else self.id,
        }
        if record.type == 'binary':
            vals.update({
                'datas': record.datas,
                'mimetype': record.mimetype,
            })
        elif record.type == 'url':
            vals.update({
                'url': record.url,
            })
        new_record = self.env['documents.document'].create(vals)
        if record.type == 'folder':
            for child in record.children_ids:
                self._copy_document_tree(child, parent=new_record)

        return new_record
