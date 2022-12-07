# -*- coding: utf-8 -*-
# Copyright 2020-2022 Sunflower IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Barcodes - Multiline",
    "summary": "It allows barcodes to span multiple lines.",
    "version": "14.0.1.0.1",
    "author": "Sunflower IT, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "barcodes",
        "web_tour",
    ],
    "demo": [
        "demo/demo_wizard.xml",
    ],
    "data": [
        "views/assets.xml",
        "views/tour_views.xml",
    ],
    "installable": True,
}
