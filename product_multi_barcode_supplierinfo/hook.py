# Copyright 2022 ForgeFlow S.L
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api


def copy_barcode(cr):
    """Copy barcode values to later create product.barcode record with them"""
    logger = logging.getLogger(__name__)
    logger.info("Copy barcode column")
    cr.execute(
        """ALTER TABLE product_supplierinfo ADD COLUMN IF NOT EXISTS old_barcode VARCHAR"""
    )
    cr.execute(
        """ UPDATE product_supplierinfo SET old_barcode = barcode
            WHERE barcode is not NULL
     """
    )


def update_barcodes_ids(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        cr.execute(
            """ UPDATE product_supplierinfo SET barcode = old_barcode
                WHERE old_barcode is not NULL
         """
        )
        supplierinfos = env["product.supplierinfo"].search([("barcode", "!=", False)])
        prod_barcode = env["product.barcode"]
        for supplierinfo in supplierinfos:
            barcode_dict = {
                "name": supplierinfo.barcode,
                "product_tmpl_id": supplierinfo.product_tmpl_id.id,
                "supplier_id": supplierinfo.name.id,
            }
            if supplierinfo.product_id:
                barcode_dict["product_id"] = supplierinfo.product_id.id
            prod_barcode.create(barcode_dict)
    return
