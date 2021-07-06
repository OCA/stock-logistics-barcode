# Copyright 2004-2011 Tiny SPRL (<http://tiny.be>)
# Copyright 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product GTIN EAN8 EAN13 UPC JPC Support",
    "version": "13.0.1.0.0",
    "author": "ChriCar Beteiligungs- und Beratungs- GmbH, "
    "Odoo Community Association (OCA), "
    "ACSONE SA/NV",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": ["product"],
    "summary": "This module provides checks and management to EAN codes",
    "data": ["views/res_config_settings_views.xml"],
    "external_dependencies": {"python": ["barcodenumber"]},
    "installable": True,
}
