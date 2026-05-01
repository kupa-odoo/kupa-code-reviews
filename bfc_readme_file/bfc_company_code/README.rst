BFC Company Code
================

This module manages automatic generation and validation of 4-digit Company Codes.

It overrides the Company Code field from the custom module ``favorite_company_selector`` and ensures uniqueness, format validation, and automatic sequencing.

This module adds validation rules and default value logic for company code management.

Creates/Overrides field in ``res.company``:

- ``company_code``: Alphanumeric field with following constraints:

  - Must be unique across all company records
  - Must contain exactly 4 alphanumeric characters

**Table of contents**

.. contents::
   :local:

Dependencies
============

This module depends on the following modules:

- ``favorite_company_selector``

Usage
=====

This module provides the following features:

1. Automatic Company Code Generation

When creating a new company (mandant), the system automatically suggests the next available 4-digit numeric code.

Logic:

- The system checks existing company codes
- Identifies the highest numeric value
- Generates the next sequence

Example:

- If the highest existing code is ``0012``
- The system will suggest ``0013``

2. Company Code Validation

The system enforces the following constraints:

- Code must be exactly 4 characters long
- Only alphanumeric values are allowed
- Code must be unique across all companies

- Prevents duplicate or invalid company codes
- Ensures consistency across the system

Credits
=======

Author
------

- Odoo PS

License
-------

This module is licensed under LGPL-3.
