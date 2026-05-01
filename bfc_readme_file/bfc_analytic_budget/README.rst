===================
BFC Analytic Budget
===================

This module extends the analytic budget functionality and introduces advanced project-related analytic account logic.

It enhances:

- Budget tracking
- Approval workflows
- Project-based analytic account structures

The module also adds new fields, models, computed logic, and approval workflows.

Table of Contents
=================

.. contents::
   :local:

Dependencies
============

This module depends on the following modules:

- ``account_budget_purchase``
- ``analytic``
- ``contacts``
- ``project``
- ``favorite_company_selector``

Configuration
=============

After installing the module:

- Assign users to the ``Analytic Budget Releaser`` group to allow budget approval.
- Configure Cost Groups from:

  ``Accounting → Configuration → Cost Groups``

Usage
=====

Budget Line Enhancements
------------------------

This module extends the ``budget.line`` model with the following fields:

- ``project_budget``:
  Base budget entered manually.

- ``expected_additional_value``:
  Additional expected amount entered manually.

- ``forecast``:
  Computed remaining forecast amount.

Forecast Calculation
~~~~~~~~~~~~~~~~~~~~

The forecast amount is calculated using the following formula:

``Forecast = Budgeted Amount - Committed Amount``

These fields are available in:

- Budget Form View
- Budget Report

Budget Approval Workflow
------------------------

This module introduces a controlled budget approval workflow.

Analytic Budget Releaser Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only users assigned to the ``Analytic Budget Releaser`` group can approve budgets.

Request for Approval
~~~~~~~~~~~~~~~~~~~~

When a budget approval request is submitted:

- A To-Do activity is created for users in the
  ``Analytic Budget Releaser`` group.
- Approvers are notified that a budget approval is required.

Approve Budget
~~~~~~~~~~~~~~

The ``Approve Budget`` action:

- Is visible only to authorized users.
- Changes the budget state to ``Open`` after approval.

This workflow ensures a controlled and traceable budget release process.

Project-Based Analytic Fields
-----------------------------

The following fields are added for project-related analytic accounts:

- ``project_number``

  - Maximum length: 10 characters
  - Must start with ``B-``

- ``master_project``

  - Computed field
  - Contains the first six characters of the project number

Example:

- ``B-0239`` from ``B-0239-011``

Cost Group Model
----------------

This module introduces a new model:

- ``analytic.cost.group``

Menu Location
~~~~~~~~~~~~~

``Accounting → Configuration → Cost Groups``

Typical fields include:

- Code
- Description

Analytic Account Naming Logic
-----------------------------

When the project-related option is enabled, the following fields are used to generate the analytic account name:

- ``Project Number``
- ``Cost Allocation`` (Selection)
- ``Sub Project Number`` (Computed)

  - First 2 characters of the Cost Allocation
  - Last 2 characters of the Project Number

- ``Company Code``

  - Derived from the company configuration

- ``Department`` (Selection)

- ``Cost Group`` (Many2one → ``analytic.cost.group``)

- ``Cost Group Code`` (Computed)
- ``Cost Group Description`` (Computed)

- ``Individual Extension Code``

  - Maximum 3 characters
  - Alphanumeric

- ``Individual Extension Description``

  - Maximum 50 characters

Analytic Account Name Structure
-------------------------------

Example:

``B-0239-011-0914AC325.3 Fliesenarbeiten``

Structure:

- ``B-0239``

  - First six characters of the project number

- ``-011``

  - Sub project number

- ``0914``

  - Company code

- ``AC``

  - Department code

Code Logic
~~~~~~~~~~

- If ``Individual Extension Code`` is provided, it is used in the analytic account name.
- Otherwise, the ``Cost Group Code`` is used.

Description Logic
~~~~~~~~~~~~~~~~~

- If ``Individual Extension Description`` is provided, it is used in the analytic account name.
- Otherwise, the ``Cost Group Description`` is used.

The analytic account name is generated automatically based on the configured project structure fields.

This naming structure ensures standardized and meaningful analytic account names across projects.

Credits
=======

Author
------

- Odoo PS

License
=======

This module is licensed under LGPL-3.
