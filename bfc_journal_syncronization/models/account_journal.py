# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
import logging
from markupsafe import Markup

from odoo import api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


SYNC_FIELDS = [
    'type',
    'name',
    'code',
    'refund_sequence',
    'debit_sequence',
    'invoice_reference_type',
    'invoice_reference_model',
    'restrict_mode_hash_table',
    'active'
]

ALLOWED_JOURNAL_TYPES = ['sale', 'purchase', 'general']


class AccountJournal(models.Model):
    _inherit = "account.journal"

    parent_journal_id = fields.Many2one(comodel_name="account.journal", string="Parent Journal", ondelete="cascade")
    child_journal_ids = fields.One2many(
        comodel_name="account.journal",
        inverse_name="parent_journal_id",
        string="Child journals",
        context={"active_test": False},
        store=True
    )
    has_master_company = fields.Boolean(related="company_id.is_master_company", string="Master company Account", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if self.env.context.get("skip_company_sync"):
            return records

        all_companies = self.env["res.company"].search([])
        master_company = all_companies.filtered(lambda c: c.is_master_company)[:1]

        if not master_company:
            return records
        child_companies = all_companies - master_company
        if not child_companies:
            return records

        Journal = self.with_context(
            skip_company_sync=True,
            allowed_company_ids=all_companies.ids,
        )
        master_accounts = records.mapped("default_account_id")

        account_map = self._map_accounts_by_company(
            master_accounts,
            all_companies.ids
        )

        vals_to_create = []

        for journal in records.filtered(
            lambda j: j.company_id.id == master_company.id and j.type in ALLOWED_JOURNAL_TYPES
        ):
            synced_vals = {field: journal[field] for field in SYNC_FIELDS}

            base_vals = {
                "parent_journal_id": journal.id,
                **synced_vals,
            }

            for company in child_companies:
                child_default_account_id = self._get_child_account_id(
                    journal.default_account_id,
                    account_map,
                    company
                ) or False
                child_account_vals = {
                    "company_id": company.id,
                    "default_account_id": child_default_account_id,
                    **base_vals,
                }
                child_account_vals["currency_id"] = journal.currency_id.id if journal.currency_id else False
                vals_to_create.append(child_account_vals)

        if vals_to_create:
            Journal.create(vals_to_create)
        return records

    def unlink(self):
        # Prevent recursion
        if self.env.context.get("skip_company_sync"):
            return super().unlink()
        all_companies = self.env["res.company"].search([])
        return super().with_context(allowed_company_ids=all_companies.ids, skip_company_sync=True).unlink()

    def action_sync_to_child_journals(self):
        """
        Sync fields of master Journal to its corresponding child
        Journas in all the companies.
        """
        all_companies = self.env["res.company"].search([])
        journals = self.sudo().with_context(allowed_company_ids=all_companies.ids)
        master_accounts = journals.mapped("default_account_id")
        account_map = self._map_accounts_by_company(
            master_accounts,
            all_companies.ids
        )

        for journal in journals.filtered(lambda j: j.child_journal_ids):
            for child in journal.child_journal_ids:
                child_company = child.company_id
                child_default_account_id = self._get_child_account_id(
                    journal.default_account_id,
                    account_map,
                    child.company_id
                )
                if child_default_account_id is None:
                    child.message_post(
                        body=Markup(f"""
                            <div>
                                <strong>Journal Sync Skipped</strong><br/><br/>
                                <strong>Company:</strong> {child.company_id.display_name}<br/>
                                <strong>Reason:</strong> No matching account found.<br/><br/>
                                <strong>Suggested Action:</strong><br/>
                                Run <em>Account Sync (Server Action)</em> first, then retry <em>Journal Sync</em>.
                            </div>
                        """)
                    )
                    continue

                vals = {field: journal[field] for field in SYNC_FIELDS}
                vals["currency_id"] = journal.currency_id.id if journal.currency_id else False
                vals["company_id"] = child_company.id if child_company else False
                vals['default_account_id'] = child_default_account_id
                child.with_company(child_company).sudo().write(vals)

    def _link_parent_journals_to_master(self, master_company):
        """Form parent-child account relations in master company."""
        if not master_company:
            raise UserError(self.env._("Please define master company first!"))

        Company = self.env["res.company"]
        all_companies = Company.search([])

        # Ensure only one master company
        master_companies = all_companies.filtered(lambda c:c.is_master_company and c.id != master_company.id)
        master_companies.is_master_company = False

        Journal = (
            self.env["account.journal"].sudo().with_context(allowed_company_ids=all_companies.ids, active_test=False)
        )

        master_journals = master_company.sudo().with_context(
            allowed_company_ids=all_companies.ids,
        ).journal_ids

        if not master_journals:
            return

        master_map = {journal.code : journal.id for journal in master_journals}

        if not master_map:
            return

        child_companies = all_companies - master_company
        child_journals = child_companies.with_context(
            allowed_company_ids=all_companies.ids
        ).mapped('journal_ids')

        if not child_journals:
            return

        child_journals_by_company = {}
        for journal in child_journals:
            company = journal.company_id
            if not company:
                continue
            child_journals_by_company.setdefault(company.id, []).append(journal.id)

        to_write = {}  # parent_id -> [child_account_ids]

        for company_id, journal_ids in child_journals_by_company.items():
            company = Company.browse(company_id)

            journals_in_company = Journal.with_company(company).browse(journal_ids)

            for child in journals_in_company:
                parent_id = master_map.get(child.code)
                if parent_id and child.parent_journal_id.id != parent_id:
                    to_write.setdefault(parent_id, []).append(child.id)

        for parent_id, child_ids in to_write.items():
            Journal.browse(child_ids).write({"parent_journal_id": parent_id})

    def _map_accounts_by_company(self, master_accounts, all_company_ids):
        """
        Build mapping for multiple master accounts at once.

        Returns:
            {
                master_account_id: {company_id: account_record}
            }
        """
        if not master_accounts:
            return {}

        accounts = self.env["account.account"].sudo().with_context(
            allowed_company_ids=all_company_ids
        ).browse(master_accounts.ids)
        accounts |= accounts.with_context(
            allowed_company_ids=all_company_ids
        ).child_account_ids

        # result[master_id][company_id] returns mapped account or False.
        result = defaultdict(lambda: defaultdict(lambda: False))

        for acc in accounts:
            if len(acc.company_ids) != 1:
                _logger.warning(
                    "Account '%s' (id=%s) belongs to %s companies - skipping.",
                    acc.display_name,
                    acc.id,
                    len(acc.company_ids),
                )
                continue

            # determine which master this account belongs to
            master_id = acc.parent_account_id.id or acc.id
            result[master_id][acc.company_ids.id] = acc

        return {k: dict(v) for k, v in result.items()}

    def _get_child_account_id(self, master_account, account_map, company):
        if not master_account:
            return False

        mapped_accounts = account_map.get(master_account.id, {})
        acc = mapped_accounts.get(company.id)

        return acc.id if acc else None
