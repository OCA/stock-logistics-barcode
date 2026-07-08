/* @odoo-module */

import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";
import {patch} from "@web/core/utils/patch";

const _origOnBarcodeScanned = BarcodeHandlerField.prototype.onBarcodeScanned;

patch(BarcodeHandlerField.prototype, {
    onBarcodeScanned(event) {
        if (typeof _origOnBarcodeScanned === "function") {
            _origOnBarcodeScanned.call(this, event);
        }
        const resModel = this.props?.record?.resModel || "";
        if (resModel.includes("wiz.stock.barcodes.read")) {
            const btn = document.getElementById("dummy_on_barcode_scanned");
            if (btn instanceof HTMLElement) {
                btn.click();
            }
        }
    },
});
