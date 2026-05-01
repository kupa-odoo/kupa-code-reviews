BFC Tax Exemption Reminder
=========================

This module manages tax exemption tracking and automated reminders for vendors and purchase operations.

It introduces exemption-related fields, automated To-Do activity creation based on expiry dates, and vendor validation warnings during Purchase Order vendor is changed.

This module adds new fields and business logic to support tax exemption compliance.

Creates new fields in ``res.partner`` (or relevant model):

- ``exemption_required``: Boolean field to indicate if exemption is required
- ``exemption_available``: Boolean field to indicate if exemption is available
- ``date_of_exemption``: Date field representing when exemption is granted
- ``expiry_of_exemption``: Date field representing when exemption expires
- ``reminder_lead_time``: Integer field (days) to define reminder trigger timing

**Table of contents**

.. contents::
   :local:

Dependencies
============

This module depends on the following modules:

- ``purchase``
- ``contacts``

Configuration
=============

After installation, configure exemption settings for vendors.

On Vendor form, you can configure:

- ``Exemption Required``
- ``Exemption Available``
- ``Date of Exemption``
- ``Expiry of Exemption``
- ``Reminder Lead Time (days)``

To enable reminder functionality:

1. Set ``Exemption Required`` as True where applicable.
2. Provide ``Expiry of Exemption`` date.
3. Define ``Reminder Lead Time (days)``.
4. Ensure a responsible user is assigned for activity notifications.

Usage
=====

This module provides the following features:

1. Automatic To-Do Activity Creation

A To-Do activity is automatically created for the responsible user when the following condition is met:

Condition:
Today's Date ≥ (Expiry of Exemption − Reminder Lead Time)

- Helps users track upcoming expiry of exemption certificates
- Ensures timely renewal actions

2. Vendor Change Warning (Non-Blocking)

When selecting or changing a vendor on a Purchase Order, a warning is displayed (non-blocking).

Condition:

- ``Exemption Required`` = True, and
- (``Exemption Available`` = False OR ``Expiry of Exemption`` < Today)

- Alerts users about missing or expired exemption certificates
- Does not block the workflow, only warns the user

Credits
=======

Author
------

- Odoo PS

License
-------

This module is licensed under LGPL-3.
