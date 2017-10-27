.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================================================
Provide light Web app to scan products Barcode and generate Stock Inventories
=============================================================================

This module was written to extend the functionality of odoo Stock module.

This module provides a web app designed to work on a Mobile. The app allows
user to scan products and select a quantity to inventory. A draft inventory
is automatically created and updated.

Interface
=========

Authentication
--------------

The first screen asks Odoo credentials. The user should be member of the Odoo
'Warehouse / User' group.

.. image:: /mobile_app_inventory/static/src/img/01_phone_authentication.png

Data Loading
------------

Once authenticated, some datas are cached : Active Products, Stock locations
and draft inventories.

Note: This step can take a while depending on your database product size and
depending on the product extra-fields you have choosen to display. (see
Extra fields Section)

.. image:: /mobile_app_inventory/static/src/img/02_phone_data_loading.png

Inventory Selection
-------------------

Once datas are loaded, user can select an existing draft stock inventory he
want to complete.

.. image:: /mobile_app_inventory/static/src/img/04_phone_select_stock_inventory.png

Alternatively, he can create a new stock inventory, tipping an inventory name.


Location Selection
------------------

Once the inventory created (or selected), user has to select the location where
he is for the time being.

.. image:: /mobile_app_inventory/static/src/img/05_select_stock_location.png

Product Selection and Quantity Selection
----------------------------------------

Once the stock inventory is created or selected, the user can select a product,
scanning a barcode.

.. image:: /mobile_app_inventory/static/src/img/06_phone_select_product.png

If the EAN13 barcode is recognized, user has to set a quantity to inventory and
then validate.

.. image:: /mobile_app_inventory/static/src/img/07_phone_select_quantity.png

If a line with the same product (and same location) already exist, an extra
screen is display to mention wich action to. (sum quantity, or replace the old
value by the one).

.. image:: /mobile_app_inventory/static/src/img/08_phone_duplicate_lines.png

Menu
----

A menu is available in each screen that allows user to navigate between
screens.

.. image:: /mobile_app_inventory/static/src/img/03_phone_menu.png


Extra Fields
------------

In the company form, admin user can set extra fields that will be displayed
when a product is scanned. A typical use case is to display stock quantity
information.

This feature is interesting to display easily and without custom developpement
extra fields of the core, or custom extra fields.

.. image:: /mobile_app_inventory/static/src/img/res_company_configuration.png

.. image:: /mobile_app_inventory/static/src/img/07_phone_select_quantity_extra_data.png


Technical Informations
======================

Hardware
--------

This module is designed to work with

* a Browser running on a Mobile (Firefox Mobile / Chrome / ...)
* a Scan reader communicating with the mobile via Bluetooth (SPP settings)

**Implementation Sample**

* Mobile : `Samsung Galaxy Xcover 3 <http://www.samsung.com/fr/consumer/mobile-devices/smartphones/others/SM-G388FDSAXEF>`_
* Scan Reader : `KDC 400 <https://koamtac.com/kdc400-bluetooth-barcode-scanner/>`_
* Browser : `Firefox 46+ <https://www.mozilla.org/en-US/firefox/os/>`_


Used Technologies
-----------------

This module uses extra JS / CSS components.

* `Angular JS v1.1 <https://angularjs.org/>`_ 
* `Angular Translate <https://angular-translate.github.io/>`_
* `Ionic Framework <http://ionicframework.com/>`_
* `Ionic Icons <http://ionicons.com/>`_ (MIT Licensed)

* `Angular Odoo <https://github.com/hparfr/angular-odoo>`_, light Javascript
  library developped by `Akretion <http://www.akretion.com/>`_
  and `Camp To Camp <http://www.camptocamp.org/>`_

Available languages
-------------------

* English
* French

If you want to use other languages just copy past the french translation file
in the 'static/www/i18n' sub folder and propose new translation.

Similar Projects
----------------

* You could be interested by another implementation of similar features
  'stock_scanner' in the same repository.

* You could be interested by the same kind of implementation for purchase
  workflow, that allow to create a purchase_order, with mobile device,
  scanning barcode and tiping desired quantity.
  `See 'scan_to_purchase' module on GRAP github repository <https://github.com/grap/odoo-addons-mobile/tree/7.0/scan_to_purchase>`_

Configuration
=============

* Optionnaly, admin user can select extra fields to display. (see above, 'Extra Fields' Section)

* Language is displayed, depending on the languages provided by the browser.
  If you want to manually change it, you can to do so on firefox:
    * go to about:config
    * Change the value of the key 'intl.accept_languages'

Usage
=====

Once installed, assuming that your Odoo instance is accessible by the URL
http//localhost:8069/, the web app can be reached at the URL
http//localhost:8069/mobile_app_inventory/static/www/index.html

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/7.0

If you're testing this module with demo data installed, you can test scanning
(or copying values) with the following two barcodes :

* 5400313040109 : Organic Chips (Paprika)
* 4260108510016 : Organic Beer (Gluten Free)

Roadmap / Current Limits
------------------------

* Dates displays does NOT change depending of the localization of the user

* JS and CSS lib are hard included. So if many apps are developped, it could
  be great to have a generic 'web_ionic' module that have all tools to avoid
  to duplicate files

Known Issues
------------

* Due to bad design of the module 'product_multi_ean' that changes type of
  code product ean13 field from char to many2one, 'mobile_app_inventory will not
  work if 'product_multi_ean' is installed. (Products loading will fail)
  This issue will not occur in V8+, due to refactoring of 'product_multi_ean'
  that fixes this bug.
  `See the bug report on Github <https://github.com/OCA/stock-logistics-barcode/issues/52>`_

* Databases list on login view displays all databases, while only databases
  with 'mobile_app_inventory' module installed should be displayed. But this
  feature could not be implemented, due to current Odoo Core limitations

* **Firefox Ionic Bug** : The first screen allows user to select database,
  in a multi database context. This module use ionic select component, that
  doesn't not works On Firefox Mobile.
  `See the bug on Ionic Github <https://github.com/driftyco/ionic/issues/4767>`_

* **Chrome Mobile limitation** : This module plays mp3 sounds when actions is,
  done. This feature is not available for Chrome Mobile for the time being,
  cause Chrome consider that allowing to play a sound without explicit action
  of the user raises security issues.
  `See the bug on Chromium website <https://bugs.chromium.org/p/chromium/issues/detail?id=178297>`_

TEMPORARY TODO LIST
===================

* stock_inventory rename scan_ok into mobile_inventory_available.
* stock_inventory ask raphael why add_inventory_line_by_scan changed.
* product_product : fix : mobile_inventory_load_product
* web : pourquoi ça marche plus !!!

* rechecker delete lorsqu'on quitte l'application. (logout)


A valider avec Raph
-------------------
* m_stock_inventory. obliger d'utiliesr $$state, pour accéder à la liste, est-ce normal ?

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-barcode/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted it
first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Module Icon is a superposition of Odoo images of Stock module and Point of
  Sale module. See Copyrights in the original Odoo project
  https://github.com/odoo/odoo

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

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
