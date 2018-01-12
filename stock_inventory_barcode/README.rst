.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Stock Inventory Barcode
=======================

The interface provided by Odoo in the official *stock* module to make an
inventory has 2 limitations:

* it is not easy/fast to use when you have several thousand products

* you cannot use a barcode reader to scan the products

This module provides a simple and easy-to-use interface to make an
inventory with the help of a barcode reader. It is designed for the
following use case:

* no tracking via Serial Numbers

* the stock location of the inventory doesn't have children locations.

Usage
=====

On the form view of an inventory, once the inventory has been started
(State = *In Progress*), you will see a button *Start Barcode
Interface*. It will open a pop-up window that allows the user to easily
enter the inventory quantity (or update the inventory quantity, in case
the product is found a second time at a different place during the
inventory).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/10.0

Known issues / Roadmap
======================

* No tracking via Serial Number (I tried to implement it, but it makes
  the interface more complex and/or slower to use: you can't get/create
  the inventory line on the onchange of the Product field, you need to
  the Serial Number to get/create the inventory line... but you also need
  to handle the case of products that are not tracked by Serial Number,
  etc...). I have tought in depth about it, and I think that it's better
  to leave support for Serial Number outside of this module, to keep it
  simple and easy-to-use for users that don't do any tracking via Serial
  Numbers (which is the case of the point of sales).

* Doesn't support inventory on locations that have children locations.
  It is easy to add support for this, but it adds one field in the wizard,
  thus make it slower to use for the user.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-barcode/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
