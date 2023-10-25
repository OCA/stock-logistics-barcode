# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def _process_product_qty_gs1(self, product_qty):
        """Extend for custom processing of product qty."""
        return product_qty

    def _process_ai_00(self, gs1_list):
        """Packaging"""
        return self.process_barcode_packaging_id()

    def _process_ai_01(self, gs1_list):
        """Packaging"""
        return self.process_barcode_packaging_id()

    def _process_ai_02(self, gs1_list):
        """Product identification"""
        res = self.process_barcode_product_id()
        # If we did not found a product and we have not a package, maybe we
        # can try to use this product barcode as a packaging barcode
        if not res:
            # Try to get packaging 01 with product GTIN
            packaging_ai = next(filter(lambda f: f["ai"] == "01", gs1_list), False)
            if not packaging_ai:
                res = self._process_ai_01(gs1_list)
        if not res:
            # Try to get packaging 00 with product GTIN
            packaging_ai = next(filter(lambda f: f["ai"] == "00", gs1_list), False)
            if not packaging_ai:
                res = self._process_ai_00(gs1_list)
        return res

    def _process_ai_240(self, gs1_list):
        """Product identification"""
        return self.process_barcode_product_id()

    def _process_ai_10(self, gs1_list):
        """Serial/Lot identification"""
        self.lot_name = self.barcode
        return self.process_barcode_lot_id()

    def _process_ai_30(self, gs1_list):
        """Variable Qty"""
        product_qty = self._process_product_qty_gs1(float(self.barcode))
        if self.packaging_id:
            self.packaging_qty = product_qty
            self.product_qty = self.packaging_qty * self.packaging_id.qty
        else:
            self.product_qty = product_qty
        return True

    def _process_ai_37(self, gs1_list):
        """Product Qty"""
        product_qty = self._process_product_qty_gs1(float(self.barcode))
        # if self.packaging_id:
        #     product_qty = self.packaging_id.qty * product_qty
        self.product_qty = product_qty
        return True

    def _process_ai_310(self, gs1_list):
        """Net Weight"""
        self.product_qty = self._process_product_qty_gs1(float(self.barcode))
        return True

    def _process_ai_330(self, gs1_list):
        """Gross Weight"""
        self.product_qty = self._process_product_qty_gs1(float(self.barcode))
        return True

    def process_barcode(self, barcode):
        gs1_list = self.env.ref(
            "barcodes_gs1_nomenclature.default_gs1_nomenclature"
        ).parse_barcode(barcode)
        if gs1_list is None:
            return super().process_barcode(barcode)
        warning_msg_list = []
        self.message = False
        for gs1_item in gs1_list:
            self.barcode = gs1_item["value"]
            ai = gs1_item["ai"]
            if hasattr(self, "_process_ai_%s" % ai):
                res = getattr(self, "_process_ai_%s" % ai[:3])(gs1_list=gs1_list)
                if not res:
                    warning_msg_list.append(
                        self.message
                        or _("({ai}){barcode} Not found").format(
                            ai=ai, barcode=self.barcode
                        )
                    )
                    self.message = False
            else:
                warning_msg_list.append(
                    _("AI GS1 ({ai}) Not implemented").format(ai=ai)
                )
        if warning_msg_list:
            self.barcode = False
            self._set_messagge_info("info", " ".join(warning_msg_list))
            return False
        if not self.check_option_required():
            return False
        if self.is_manual_confirm or self.manual_entry:
            self._set_messagge_info("info", _("Review and confirm"))
            return False
        return self.action_confirm()
