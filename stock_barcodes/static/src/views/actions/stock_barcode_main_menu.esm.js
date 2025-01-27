/** @odoo-module **/
import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {markup} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {Component, onWillStart, useEffect} = owl;

export class StockBarcodesMainMenu extends Component {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.ormService = useService("orm");
        const busService = useService("bus_service");
        const notification = useService("notification");
        this.modelBarcodeAction = "stock.barcodes.action";
        if (this.hasService("home_menu"))
            this.homeMenuService = useService("home_menu");
        onWillStart(async () => {
            this.barcodeActions = await this.getBarcodeActions();
        });

        const handleNotification = ({detail: notifications}) => {
            if (notifications && notifications.length > 0) {
                notifications.forEach((notif) => {
                    const {payload, type} = notif;
                    if (type === "actions_main_menu_barcode") {
                        if (payload.action_ok && payload.action) {
                            this.actionService.doAction(payload.action);
                        } else {
                            notification.add(
                                _t("No action found with barcode: " + payload.barcode),
                                {
                                    type: "danger",
                                }
                            );
                        }
                    }
                });
            }
        };
        useEffect(() => {
            busService.addChannel("stock_barcodes_main_menu");
            busService.addEventListener("notification", handleNotification);
            return () => {
                busService.deleteChannel("stock_barcodes_main_menu");
                busService.removeEventListener("notification", handleNotification);
            };
        });
    }

    hasService(service) {
        return service in this.env.services;
    }

    mainMenuHome() {
        // Enterprise
        if (this.hasService("home_menu")) {
            this.homeMenuService.toggle(true);
        } else {
            // Community
            this.actionService.doAction("mail.action_discuss");
            browser.setTimeout(() => browser.location.reload(), 100);
        }
    }

    async openAction(action_id) {
        const action = await this.ormService.call(
            this.modelBarcodeAction,
            "open_action",
            [action_id]
        );
        action.help = markup(_t(action.help));
        this.actionService.doAction(action);
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
