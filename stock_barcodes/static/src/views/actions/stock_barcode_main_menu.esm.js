import {Component, markup, onWillStart, useEffect} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";

export class StockBarcodesMainMenu extends Component {
    setup() {
        this.actionService = useService("action");
        this.ormService = useService("orm");
        const busService = useService("bus_service");
        const notification = useService("notification");
        this.modelBarcodeAction = "stock.barcodes.action";
        this.homeMenuService = this.env.services.home_menu || null;
        onWillStart(async () => {
            this.barcodeActions = await this.getBarcodeActions();
        });

        // Capture the scanner input on this screen and let the server look
        // up the barcode action; the reply comes back through the
        // "actions_main_menu_barcode" bus notification handled below.
        const barcodeService = useService("barcode");
        useBus(barcodeService.bus, "barcode_scanned", (ev) =>
            this._onBarcodeScanned(ev.detail.barcode)
        );

        const handleMainMenuBarcode = (payload) => {
            if (payload.action_ok && payload.action) {
                return this.actionService.doAction(payload.action);
            }
            notification.add(_t("No action found with barcode: %s", payload.barcode), {
                type: "danger",
            });
        };
        useEffect(
            () => {
                // Subscribe() alone does not start the bus connection; make
                // sure it is running so the scanned action can be received.
                busService.start();
                busService.subscribe(
                    "actions_main_menu_barcode",
                    handleMainMenuBarcode
                );
                return () => {
                    busService.unsubscribe(
                        "actions_main_menu_barcode",
                        handleMainMenuBarcode
                    );
                };
            },
            // Subscribe once on mount: OWL default dependencies ([NaN])
            // re-apply the effect on every render
            () => []
        );
    }

    hasService(service) {
        return service in this.env.services;
    }

    async _onBarcodeScanned(barcode) {
        await this.ormService.call("wiz.stock.barcodes.read", "process_barcode", [
            [],
            barcode,
        ]);
    }

    mainMenuHome() {
        // Enterprise
        if (this.homeMenuService && this.hasService("home_menu")) {
            this.homeMenuService.toggle(true);
        } else {
            // Community
            browser.setTimeout(() => browser.location.reload(), 100);
            return this.actionService.doAction("mail.action_discuss");
        }
    }

    async openAction(action_id) {
        const action = await this.ormService.call(
            this.modelBarcodeAction,
            "open_action",
            [action_id]
        );
        action.help = markup(action.help || "");
        return this.actionService.doAction(action);
    }

    async getBarcodeActions() {
        return await this.ormService.call(this.modelBarcodeAction, "search_read", [], {
            domain: [["action_window_id", "!=", false]],
            fields: ["id", "name", "icon_class"],
        });
    }
}

StockBarcodesMainMenu.template = "stock_barcodes.MainMenu";

registry.category("actions").add("stock_barcodes_main_menu", StockBarcodesMainMenu);
