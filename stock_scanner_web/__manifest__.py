# © 2016 Angel Moya <http://angelmoya.es>
# © 2016 Eficent Business and IT Consulting Services, S.L.
#        <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Scanner Web",
    "summary": "Show scenarios from stock scanner on web app",
    "version": "12.0.1.0.0",
    "category": "Generic Modules/Inventory Control",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "author": "AngelMoya, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_scanner",
    ],
    "data": [
        "views/web_templates.xml",
        "views/scanner_hardware.xml",
        "views/warehouse_menu.xml",
        "views/res_user_view.xml",
    ],
    "demo": [
        "demo/stock_scanner_demo.xml",
        "demo/template_view.xml",
        "demo/TutorialWeb.scenario",
        "demo/Web_step_type/Web_step_type.scenario",
    ],
}
