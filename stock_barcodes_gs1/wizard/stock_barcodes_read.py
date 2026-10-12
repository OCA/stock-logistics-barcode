# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.tools import check_barcode_encoding

BARCODE_ENCODING = ["ean8", "ean13", "gtin14", "upca", "sscc"]


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
        # When the Lot/Serial is included in barcode and 'set_info_from_quants' is
        # activated we do not want get info from quants when the product is processed
        # because it will be processed in lot method.
        if self._is_lot_ai_in_barcode(gs1_list):
            self = self.with_context(skip_set_info_from_quants=True)
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
        # When the Lot/Serial is included in barcode and 'set_info_from_quants' is
        # activated we do not want get info from quants when the product is processed
        # because it will be processed in lot method.
        if self._is_lot_ai_in_barcode(gs1_list):
            self = self.with_context(skip_set_info_from_quants=True)
        return self.with_context(
            barcode_domain_field="default_code"
        ).process_barcode_product_id()

    def _process_ai_10(self, gs1_list):
        """Serial/Lot identification"""
        if self.product_id and self.product_id.tracking == "none":
            return True
        # Do not keep the lot of a previous reading when this one is not found
        self.lot_id = False
        self.lot_name = self.barcode
        # Determine if barcode scanned has included the weight to no update product_qty
        # from lot
        weight_ai = next(filter(lambda f: f["ai"].startswith("31"), gs1_list), False)
        if weight_ai:
            self = self.with_context(skip_update_quantity_from_lot=True)
        if self.process_barcode_lot_id():
            return True
        # A lot not found yet is created on confirmation when the options allow it
        return bool(
            self.option_group_id.create_lot and self.product_id and self.lot_name
        )

    def _process_ai_21(self, gs1_list):
        """Serial number identification"""
        # If lot (10) is set in gs1 avoid reprocess
        # else process serial number (21) as lot
        lot_ai = next(filter(lambda f: f["ai"].startswith("10"), gs1_list), False)
        if lot_ai:
            return True
        return self._process_ai_10(gs1_list=gs1_list)

    def _process_ai_30(self, gs1_list):
        """Variable Qty"""
        return self._set_gs1_product_qty(
            self._process_product_qty_gs1(float(self.barcode))
        )

    def _process_ai_37(self, gs1_list):
        """Product Qty"""
        return self._set_gs1_product_qty(
            self._process_product_qty_gs1(float(self.barcode))
        )

    def _set_gs1_product_qty(self, product_qty):
        """Set the quantities from a GS1 quantity AI, converting through the
        scanned packaging when any."""
        if self.packaging_id:
            self.packaging_qty = product_qty
            product_qty *= self.packaging_id.qty
        self.product_qty = product_qty
        return True

    def _process_ai_310(self, gs1_list):
        """Net Weight"""
        return self._process_gs1_weight(gs1_list, "31")

    def _process_ai_330(self, gs1_list):
        """Gross Weight"""
        return self._process_gs1_weight(gs1_list, "33")

    def _process_gs1_weight(self, gs1_list, ai_prefix):
        """Set the quantity from a weight AI when the rule allows using the
        weight as units or the product is weight based."""
        weight_ai = next(
            filter(lambda f: f["ai"].startswith(ai_prefix), gs1_list), False
        )
        if weight_ai and (
            weight_ai.get("use_weight_as_unit")
            or self.product_uom_id.category_id
            == self.env.ref("uom.product_uom_categ_kgm")
        ):
            quantity = float(self.barcode)
            rule = weight_ai.get("rule", self.env["barcode.rule"])
            weight_uom = rule.associated_uom_id
            if weight_uom and weight_uom.category_id == self.product_uom_id.category_id:
                quantity = weight_uom._compute_quantity(
                    quantity, self.product_uom_id, round=False
                )
            self.product_qty = self._process_product_qty_gs1(quantity)
        return True

    def _process_ai_15(self, gs1_list):
        """Preferred date identification. To extend by other modules"""
        return True

    def _process_ai_17(self, gs1_list):
        """expiration date identification. To extend by other modules"""
        return True

    def _hook_process_gs1_value(self, gs1_item):
        """Hook to be extended by other modules"""
        return gs1_item["value"]

    def _hook_gs1_item_changed(self, gs1_list):
        """The barcode has read another product or lot than the previous reading.
        To be extended by other modules to drop the values of the previous reading.
        """

    @staticmethod
    def _is_lot_ai_in_barcode(gs1_list):
        """Helper method to know if the Lot/Serial is included in barcode"""
        return next(filter(lambda f: f["ai"] == "10", gs1_list), False)

    @api.model
    def _ean_barcode_valid(self, barcode):
        """Check if barcode is valid and not GS1"""
        for encoding in BARCODE_ENCODING:
            if check_barcode_encoding(barcode, encoding):
                return True
        return False

    def process_barcode(self, barcode):
        nomenclature = self.env.company.nomenclature_id.filtered(
            "is_gs1_nomenclature"
        ) or self.env.ref("barcodes_gs1_nomenclature.default_gs1_nomenclature")
        gs1_list = None
        if (
            nomenclature.gs1_separator_fnc1
            and nomenclature.gs1_separator_fnc1 in barcode
            or not self._ean_barcode_valid(barcode)
        ):
            gs1_list = nomenclature.parse_barcode(barcode)
        if gs1_list is None:
            return super().process_barcode(barcode)
        warning_msg_list = []
        failed = False
        self.message = False
        previous_product = self.product_id
        previous_lot = self.lot_id.name or self.lot_name
        # Empty previous packaging wnen barcode contains 30, 37, 310, 330, etc.
        if next(filter(lambda f: f["ai"][0] == "3", gs1_list), False):
            self.packaging_id = False
        for gs1_item in gs1_list:
            self.barcode = self._hook_process_gs1_value(gs1_item)
            ai = gs1_item["ai"]
            process_ai = getattr(self, f"_process_ai_{ai[:3]}", None)
            if process_ai:
                res = process_ai(gs1_list=gs1_list)
                if not res:
                    failed = True
                    warning_msg_list.append(
                        self.message
                        or _(
                            "(%(ai)s)%(barcode)s Not found",
                            ai=ai,
                            barcode=self.barcode,
                        )
                    )
                    self.message = False
            else:
                warning_msg_list.append(_("AI GS1 (%(ai)s) Not implemented", ai=ai))
        if failed:
            # A partial reading could be confirmed on the product of the previous one
            self.product_id = False
            self.packaging_id = False
            self.action_clean_lot()
            self.product_qty = 0.0
            self.packaging_qty = 0.0
        if (previous_product and previous_product != self.product_id) or (
            previous_lot and previous_lot != (self.lot_id.name or self.lot_name)
        ):
            self._hook_gs1_item_changed(gs1_list)
        if warning_msg_list:
            self.barcode = False
            self._set_messagge_info("info", " ".join(warning_msg_list))
            for warning_msg in warning_msg_list:
                self.display_notification(
                    warning_msg, message_type="danger", title="GS-1 code"
                )
        if failed:
            self.play_sounds(False)
            return False
        if not self.with_context(
            skip_display_notification=True
        ).check_option_required():
            self.play_sounds(False)
            return False
        if self.is_manual_confirm or self.manual_entry:
            self._set_messagge_info("info", _("Review and confirm"))
            self.play_sounds(True)
            return False
        return self.action_confirm()
