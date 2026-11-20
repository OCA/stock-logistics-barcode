/* @odoo-module */

import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";
import {patch} from "@web/core/utils/patch";

const _origOnBarcodeScanned = BarcodeHandlerField.prototype.onBarcodeScanned;

/** True if the field is the barcode reader of one of the OCA scan wizards. */
export function isStockBarcodesReader(props) {
    const resModel = props?.record?.resModel || "";
    return (
        resModel.startsWith("wiz.stock.barcodes.read") &&
        props?.name === "_barcode_scanned"
    );
}

patch(BarcodeHandlerField.prototype, {
    async onBarcodeScanned(event) {
        if (!isStockBarcodesReader(this.props)) {
            // Keep the core behaviour for any other barcode handler field.
            return _origOnBarcodeScanned.call(this, event);
        }
        // The core handler does not await record.update(): wait for the
        // _barcode_scanned onchange before clicking the button, otherwise it
        // can process an empty or the previously scanned barcode.
        await this.props.record.update({
            [this.props.name]: event.detail.barcode,
        });
        const btn = document.getElementById("dummy_on_barcode_scanned");
        if (btn instanceof HTMLElement) {
            btn.click();
        }
    },
});
