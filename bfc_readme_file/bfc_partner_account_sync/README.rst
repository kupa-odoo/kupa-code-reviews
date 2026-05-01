BFC Partner Account Sync
========================

This module synchronizes partner account-related data from a master company to other companies.

It provides a server action that triggers a scheduled synchronization process (cron job) to update partner records in batches, along with chatter notifications for tracking the sync process.

Creates new logic in ``res.partner``:

- ``exclude_from_sync``: Boolean field to exclude specific company partners from synchronization

**Table of contents**

.. contents::
   :local:

Dependencies
============

This module depends on the following modules:

- ``sale_management``
- ``purchase``
- ``contacts``
- ``bfc_master_company_coa_sync``

Configuration
=============

After installation:

- Use the ``Exclude from Sync`` field on copmany form to skip specific company partners from synchronization
- Ensure proper access rights for users executing the server action

Usage
=====

This module provides the following features:

1. Server Action Trigger

- A server action is available to start the synchronization process
- On clicking the action:
  - A cron job is triggered
  - Partners are processed in batches of 100 records
  - Master company partner data is synced to other companies

2. Sync Notifications

- When synchronization starts, a message is posted in the current user's partner chatter
- When synchronization completes, a completion message is posted

- Helps track sync progress and completion status

3. Field Synchronization Logic

The following fields are synchronized based on defined rules:

- ``property_account_receivable_id``:
  - Matched using linked master account
  - Assigned if matching record is found, otherwise skipped

- ``property_account_payable_id``:
  - Matched using linked master account
  - Assigned if matching record is found, otherwise skipped

- ``property_payment_term_id``:
  - If defined for all companies → directly assigned
  - Otherwise → searched by name in child company
  - Assigned if match found, otherwise skipped

- ``property_supplier_payment_term_id``:
  - If defined for all companies → directly assigned
  - Otherwise → searched by name in child company
  - Assigned if match found, otherwise skipped

- ``property_product_pricelist``:
  - If defined for all companies → directly assigned
  - Otherwise → searched by name in child company
  - Assigned if match found, otherwise skipped

- ``property_account_position_id``:
  - If defined for all companies → directly assigned
  - Otherwise → searched by name in child company
  - Assigned if match found, otherwise skipped

- ``receipt_reminder_email``:
  - Always synchronized directly from master record

- ``reminder_date_before_receipt``:
  - Always synchronized directly from master record

Credits
=======

Author
------

- Odoo PS

License
-------

This module is licensed under LGPL-3.
