/** @odoo-module **/

/*
 * StockBarcodesFormController for Odoo 18 (compatible with 16/17).
 *
 * Goals:
 * - Provide a public method `openBarcodeScanner()` that starts scanning via the
 *   (optional) "barcode" service when available, with graceful fallback.
 * - Emit an app-level event on successful scans so other parts (renderer, model,
 *   kanban list, etc.) can react without tight coupling.
 * - Ensure proper cleanup on unmount / navigation to avoid leaks.
 *
 * OCA-friendly: uses public services/hooks only (no private APIs).
 */

import {FormController} from "@web/views/form/form_controller";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";
import {useEffect} from "@odoo/owl";

export class StockBarcodesFormController extends FormController {
    setup() {
        super.setup();

        // Public services (safe across 16/17/18)
        this.notification = useService("notification");
        this.action = useService("action");
        this.ui = useService("ui");

        // Barcode service is optional (exists if stock_barcode or similar is loaded).
        // Keep it guarded so the controller works even without that module.
        this.barcode = null;
        try {
            this.barcode = useService("barcode");
        } catch {
            // Service not available; fall back gracefully
            this.barcode = null;
        }

        // Track stop handler for cleanup if barcode service is in use
        this._stopBarcode = null;

        // Defensive cleanup on page/tab visibility or component teardown
        useEffect(
            () => {
                const onVisibilityChange = () => {
                    if (document.hidden) {
                        this._stopScannerIfAny();
                    }
                };
                document.addEventListener("visibilitychange", onVisibilityChange, true);

                return () => {
                    document.removeEventListener(
                        "visibilitychange",
                        onVisibilityChange,
                        true
                    );
                    this._stopScannerIfAny();
                };
            },
            () => []
        );
    }

    /**
     * Public: open the barcode scanner.
     * Prefer the "barcode" service when available, otherwise warn the user.
     */
    async openBarcodeScanner() {
        // If a scanner is already running, stop and restart for a clean session.
        this._stopScannerIfAny();

        if (this.barcode && typeof this.barcode.start === "function") {
            // Start service-based scanning
            const stop = this.barcode.start({
                // Called on every successful scan
                onBarcodeScanned: (payload) => {
                    // Some impls pass a raw string, others an object { barcode, ... }
                    const code =
                        typeof payload === "string" ? payload : payload?.barcode || "";
                    if (!code) {
                        this._notifyWarn(_t("Empty barcode."));
                        return;
                    }
                    this.onBarcodeScanned(code);
                },
                // Error callback for camera/permission issues, etc.
                onError: (err) => {
                    this.onBarcodeError(err);
                },
            });
            this._stopBarcode = typeof stop === "function" ? stop : null;
            this._notifyInfo(_t("Scanner started. Press Esc or switch tab to stop."));
            return;
        }

        // Fallback: no service available
        this._notifyWarn(
            _t(
                "No barcode service available. Install/enable stock_barcode or use a hardware wedge scanner."
            )
        );
    }

    /**
     * Hook: called when a barcode has been scanned.
     * Default behavior is to emit an event that others can subscribe to.
     * Override this to implement custom search/write/open flows.
     */
    onBarcodeScanned(code) {
        // Emit an application-level event so renderer or parent components can handle it.
        // Consumers can listen to: env.bus.on("stock_barcodes:scan", (evt) => {...})
        const payload = {
            code,
            model: this.props?.resModel || null,
            resId: this.props?.resId || null,
            viewType: "form",
        };
        this.env.bus.trigger("stock_barcodes:scan", payload);

        // Optional UX hint
        this._notifySuccess(_t("Scanned: %s").replace("%s", code));
    }

    /**
     * Hook: called when the barcode service reports an error.
     */
    onBarcodeError(err) {
        const msg =
            (err && (err.message || err.toString?.())) || _t("Barcode scan error.");
        this._notifyDanger(msg);
        this._stopScannerIfAny();
    }

    /**
     * Ensure we stop the scanner on navigation.
     * Odoo calls beforeLeave() in several flows; we keep it defensive.
     */
    async beforeLeave() {
        this._stopScannerIfAny();
        if (super.beforeLeave) {
            return super.beforeLeave();
        }
    }

    // -----------------------------
    // Internal helpers
    // -----------------------------

    _stopScannerIfAny() {
        if (typeof this._stopBarcode === "function") {
            try {
                this._stopBarcode();
            } catch {
                // Ignore
            }
        }
        this._stopBarcode = null;
    }

    _notifyInfo(message) {
        this.notification.add(message, {type: "info"});
    }
    _notifyWarn(message) {
        this.notification.add(message, {type: "warning"});
    }
    _notifyDanger(message) {
        this.notification.add(message, {type: "danger"});
    }
    _notifySuccess(message) {
        this.notification.add(message, {type: "success"});
    }
}
