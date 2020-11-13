# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multiple EAN13 on products",
    "version": "12.0.1.0.3",
    "license": "AGPL-3",
    "author": "Camptocamp, "
    "Trey, "
    "Tecnativa, "
    "QubiQ, "
    "Odoo Community Association (OCA)",
    "category": "Product Management",
    "depends": [
        "product",
    ],
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "data": [
        "views/product_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
