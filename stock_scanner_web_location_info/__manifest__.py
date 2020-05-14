# © 2011-2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# © 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Scanner Web Location Info",
    "summary": "This module installs a scenario which displays "
               "the information about a location",
    "version": "11.0.1.0.0",
    "category": "Generic Modules/Inventory Control",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "author": "PESOL,"
              "SYLEAM,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_scanner_web",
    ],
    "data": [
        "data/Stock.scenario",
        "data/Location_informations/Location_informations.scenario",
        "views/template_view.xml",
    ],
    "images": [
        "images/scanner_scenario.png",
    ],
}
