BFC Analytic Budget
===================

This module extends analytic budget functionality and introduces advanced project-related analytical account logic.

It enhances budget tracking, approval workflows, and analytic account structuring with project-based configurations.

This module adds new fields, models, computed logic, and approval workflows.

**Table of contents**

.. contents::
   :local:

Dependency
============

This module depends on the following modules:

- ``account_budget_purchase``
- ``analytic``
- ``contacts``
- ``project``
- ``favorite_company_selector``

Configuration
=============

After installation:

- Assign users to the group ``Analytic Budget Releaser`` to allow budget approval
- Configure Cost Groups from:
  Accounting → Configuration → Cost Groups

Usage
=====

This module provides the following features:

-----------------------------------
1. Budget Line Enhancements
-----------------------------------

Adds new fields in ``budget.line``:

- ``project_budget``: Manually entered field (Base Budget)
- ``expected_additional_value``: Manually entered field
- ``forecast``: Computed field

Forecast Calculation:

- ``Forecast = Budgeted Amount − Committed Amount``

- All three fields are displayed in:
  - Budget Form View
  - Budget Report

-----------------------------------
2. Budget Approval Workflow
-----------------------------------

Introduces a controlled approval process:

- ``Analytic Budget Releaser`` group:
  - Only users in this group can approve budgets

Actions:

**Request for Approval**

- Creates a To-Do activity for authorized users
- Notifies approvers that budget approval is required

**Approve Budget**

- Visible only to authorized users
- On click:
  - Budget state changes to ``Open``

- Ensures controlled and trackable budget release process

-----------------------------------
3. Project-Based Analytic Fields
-----------------------------------

Adds new fields:

- ``project_number``:
  - Maximum 10 characters
  - Must start with ``B-``

- ``master_project``:
  - Computed field
  - First 6 characters of Project Number

-----------------------------------
4. Cost Group Model
-----------------------------------

Creates new model:

- ``analytic.cost.group``

Menu:

- Accounting → Configuration → Cost Groups

Fields typically include:

- Code
- Description

-----------------------------------
5. Analytic Account Naming Logic
-----------------------------------

When ``Project Related`` is enabled, the following fields are used:

- ``Project Number``
- ``Cost Allocation`` (Selection)
- ``Sub Project Number`` (Computed):
  - First 2 characters of Cost Allocation
  - Last 2 characters of Project Number

- ``Company Code``:
  - Derived from company

- ``Department`` (Selection)

- ``Cost Group`` (Many2one → analytic.cost.group)

- ``Cost Group Code`` (Computed)
- ``Cost Group Description`` (Computed)

- ``Individual Extension Code``:
  - Max 3 characters
  - Alphanumeric

- ``Individual Extension Description``:
  - Max 50 characters

-----------------------------------
6. Analytic Account Name Structure
-----------------------------------

Example:

``B-0239-011-0914AC325.3 Fliesenarbeite``

Structure:

- ``B-0239`` → First 6 characters of Project Number
- ``-011`` → Sub Project Number
- ``0914`` → Company Code
- ``AC`` → Department

Code Logic:

- If Individual Extension Code exists → use it
- Otherwise → use Cost Group Code

Description Logic:

- If Individual Extension Description exists → use it
- Otherwise → use Cost Group Description

- Ensures standardized and meaningful analytic account naming

Credits
=======

Author
------

- Odoo PS

License
-------

This module is licensed under LGPL-3
