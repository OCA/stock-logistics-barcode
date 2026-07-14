/* Copyright 2019 ForgeFlow S.L.
 * Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";
import {patch} from "@web/core/utils/patch";

function waitButtonsEnabled(selector, timeout = 2000) {
    return new Promise((resolve) => {
        if (!document.querySelector(`${selector}[disabled]`)) {
            resolve();
            return;
        }
        const observer = new MutationObserver(() => {
            if (!document.querySelector(`${selector}[disabled]`)) {
                observer.disconnect();
                resolve();
            }
        });
        observer.observe(document.body, {
            subtree: true,
            childList: true,
            attributes: true,
            attributeFilter: ["disabled"],
        });
        setTimeout(() => {
            observer.disconnect();
            resolve();
        }, timeout);
    });
}

patch(BarcodeHandlerField.prototype, {
    async onBarcodeScanned(event) {
        super.onBarcodeScanned(event);
        await this.props.record.model.mutex.exec(() => {
            // Queue turn only: wait for the scan to be processed.
        });
        await waitButtonsEnabled(".barcode-automatic-entry");
        for (const button of document.querySelectorAll(
            ".barcode-automatic-entry:not([disabled])"
        )) {
            button.click();
        }
    },
});
