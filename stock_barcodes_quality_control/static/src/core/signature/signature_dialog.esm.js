/** @odoo-module */

import {SignatureDialog} from "@web/core/signature/signature_dialog";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";

patch(SignatureDialog.prototype, {
    onClickConfirm() {
        super.onClickConfirm();
        browser.setTimeout(() => {
            this.env.bus.trigger("STOCK_BARCODES:SIGN-UPDATED");
        }, 5000);
    },
});
