BFC Journal Synchronization
===============================

This module synchronizes Journals from one master company
to other companies in a multi-company environment.

It provides journal mapping, synchronization actions, and
updates between master and child companies.

This module extends journal synchronization functionality
to ensure consistency across companies.

**Table of contents**

.. contents::
   :local:

Dependencies
============

This module depends on the following modules:

- ``account_debit_note``
- ``bfc_master_company_coa_sync``

Configuration
=============

After installation, configure the master company from Companies.

On Company, you can configure:

- ``Master Company``

To use synchronization:

1. Open the company that should be the master company.
2. Enable ``Master Company``.
3. Give users the ``Account Sync Rights`` group if needed.
4. Use ``Map Company Journals`` to link existing child company journals.
5. Use ``Sync Journals With Master Company`` to sync journals.

Usage
=====

This module allows users to:

- synchronize journals from master company to child companies
- map existing child company journals with master journals
- update journals across companies

Features
========

**Sync Journals With Master Company**

When this button is clicked:

- The system checks whether a journal with the same sequence prefix exists in the child company.
- If found, the existing journal is updated to match the master company journal.
- If not found, a new journal is created and mapped to the master journal.

**Map Company Journals**

- This button allows mapping of journals between master and child companies.

**Sync All Journals**

- When journals in the master company are updated, this action updates all mapped journals in child companies.

Example
=======

**Child Company (Before Sync)**

- Name: ABCD
- Sequence Prefix: INV
- Type: Sale
- Company: Company 2

**Master Company (Your Company)**

Journal 1:

- Name: Sales
- Sequence Prefix: INV
- Type: Sale
- Company: Your Company

Journal 2:

- Name: Purchases
- Sequence Prefix: BILL
- Type: Purchase
- Company: Your Company

**Synchronization Process**

When the server action is triggered:

1. The system checks for a journal with the same sequence prefix in the child company.
2. If a match is found (e.g., ``INV``), the journal is updated.
3. If no match is found (e.g., ``BILL``), a new journal is created.

**Child Company (After Sync)**

Journal 1:

- Name: Sales
- Sequence Prefix: INV
- Type: Sale
- Company: Company 2

Journal 2:

- Name: Purchases
- Sequence Prefix: BILL
- Type: Purchase
- Company: Company 2

Credits
=======

Author
------

- Odoo PS

License
-------

This module is licensed under LGPL-3.
