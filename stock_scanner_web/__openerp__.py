# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Scanner Web",
    "summary": "Responsive web to work with stock scanner scenarios",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "application": False,
    "installable": True,
    "license": "AGPL-3",
    "depends": [
        "stock_scanner",
    ],
    "data": [
        "view/warehouse_menu.xml",
        "view/web_templates.xml",
        "view/res_user_view.xml",
    ]
}
