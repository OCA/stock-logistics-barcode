/* @odoo-module */

import {useEffect} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {patch} from "@web/core/utils/patch";
import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";

const _origSetup = BarcodeHandlerField.prototype.setup;
const _origOnBarcodeScanned = BarcodeHandlerField.prototype.onBarcodeScanned;

patch(BarcodeHandlerField.prototype, {
    setup() {
        if (typeof _origSetup === "function") {
            _origSetup.call(this, ...arguments);
        }

        // Services en 18.0
        this.busService = useService("bus_service");
        this.orm = useService("orm");

        // Handler estable (misma referencia para subscribe/unsubscribe)
        this._onBusNotification = async (notifications = []) => {
            for (const {type} of notifications) {
                if (type === "stock_barcodes_refresh_data") {
                    const model = this.env?.model || this.props?.record?.model;
                    const rootModel = model?.root || this.env?.model?.root;
                    if (rootModel?.load) {
                        await rootModel.load();
                    }
                    if (model?.notify) {
                        model.notify();
                    }
                }
            }
        };

        // Importante en OWL v2: deps como función que devuelve []
        useEffect(
            () => {
                // Suscribir al canal y al evento correcto
                this.busService.addChannel("barcode_reload");
                this.busService.addEventListener(
                    "notification",
                    this._onBusNotification
                );

                // Limpieza
                return () => {
                    this.busService.deleteChannel("barcode_reload");
                    this.busService.removeEventListener(
                        "notification",
                        this._onBusNotification
                    );
                };
            },
            () => []
        );
    },

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
