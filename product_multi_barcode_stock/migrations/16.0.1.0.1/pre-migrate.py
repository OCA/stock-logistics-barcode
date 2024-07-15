from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.update_module_names(
        cr,
        [
            ("product_multi_barcode_stock_menu", "product_multi_barcode_stock"),
        ],
        merge_modules=False,
    )
