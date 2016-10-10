# -*- coding: utf-8 -*-
# Copyright 2016 Angel Moya <http://angelmoya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Scanner Web",
    "summary": "Show scenarios from stock scanner on web app",
    "version": "9.0.1.0.0",
    "category": "Warehouse",
    "website": "https://odoo-community.org/",
    "author": "AngelMoya, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_scanner",
    ],
    "data": [
        "views/web_templates.xml",
    ],
}
