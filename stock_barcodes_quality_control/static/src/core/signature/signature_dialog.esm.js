/** @odoo-module */

import {SignatureDialog} from "@web/core/signature/signature_dialog";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";

patch(SignatureDialog.prototype, "stock_barcodes_quality_control.SignatureDialog", {
    onClickConfirm() {
        this._super();
        browser.setTimeout(() => {
            this.env.bus.trigger("STOCK_BARCODES:SIGN-UPDATED");
        }, 5000);
    },
});
