/** @odoo-module */
/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {onPatched, useEffect, useRef} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {isAllowedBarcodeModel} from "../../utils/barcodes_models_utils.esm";
import {patch} from "@web/core/utils/patch";
import {useHotkey} from "@web/core/hotkeys/hotkey_hook";

patch(KanbanRenderer.prototype, "stock_barcodes.KanbanRenderer", {
    setup() {
        const rootRef = useRef("root");
        useHotkey(
            "Enter",
            ({target}) => {
                if (!target.classList.contains("o_kanban_record")) {
                    return;
                }

                // Open first link
                let firstLink = null;
                if (isAllowedBarcodeModel(this.props.list.resModel)) {
                    firstLink = target.querySelector(
                        ".oe_kanban_action_button,.oe_btn_quick_action"
                    );
                }
                if (!firstLink) {
                    firstLink = target.querySelector(
                        ".oe_kanban_global_click, a, button"
                    );
                }
                if (firstLink && firstLink instanceof HTMLElement) {
                    firstLink.click();
                }
                return;
            },
            {area: () => rootRef.el}
        );

        this._super(...arguments);
        this.ormService = useService("orm");
        this.action = useService("action");
        const busService = useService("bus_service");
        this.enableCurrentOperation = 0;
        const handleNotification = ({detail: notifications}) => {
            if (notifications && notifications.length > 0) {
                notifications.forEach((notif) => {
                    const {payload, type} = notif;
                    if (type === "enable_operations" && payload) {
                        this.enableCurrentOperation = payload.id;
                    }
                });
            }
        };
        useEffect(() => {
            busService.addChannel("stock_barcodes_kanban_update");
            busService.addEventListener("notification", handleNotification);
            return () => {
                busService.deleteChannel("stock_barcodes_kanban_update");
                busService.removeEventListener("notification", handleNotification);
            };
        });

        onPatched(() => {
            $("div.oe_kanban_operations-" + this.enableCurrentOperation).removeClass(
                "d-none"
            );
        });

        if (isAllowedBarcodeModel(this.props.list.resModel)) {
            if (this.env.searchModel) {
                useBus(this.env.searchModel, "focus-view", () => {
                    const {model} = this.props.list;
                    if (model.useSampleModel || !model.hasData()) {
                        return;
                    }
                    const cards = Array.from(
                        rootRef.el.querySelectorAll(".o_kanban_record")
                    );
                    const firstCard = cards.find(
                        (card) =>
                            card.querySelectorAll("button[name='action_barcode_scan']")
                                .length > 0
                    );
                    if (firstCard) {
                        // Focus first kanban card
                        firstCard.focus();
                    }
                });
            }
        }

        this.showMessageScanProductPackage =
            this.props.list.resModel === "stock.picking";
    },

    getNextCard(direction, iCard, cards, iGroup, isGrouped) {
        let nextCard = null;
        switch (direction) {
            case "down":
                nextCard = iCard < cards[iGroup].length - 1 && cards[iGroup][iCard + 1];
                break;
            case "up":
                nextCard = iCard > 0 && cards[iGroup][iCard - 1];
                break;
            case "right":
                if (isGrouped) {
                    nextCard = iGroup < cards.length - 1 && cards[iGroup + 1][0];
                } else {
                    nextCard = iCard < cards[0].length - 1 && cards[0][iCard + 1];
                }
                break;
            case "left":
                if (isGrouped) {
                    nextCard = iGroup > 0 && cards[iGroup - 1][0];
                } else {
                    nextCard = iCard > 0 && cards[0][iCard - 1];
                }
                break;
        }
        return nextCard;
    },

    // eslint-disable-next-line complexity
    // This is copied from the base kanban_renderer.
    // We want to only focus card with barcode when isAllowedBarcodeModel returns true
    // Since there is no way to hook and change the candidate cards that are selectable
    // (cards line 84) we cannot inherit and change the result. And even if we called
    // super it would not respect inheritability
    /**
     * Redefines focusNextCard to select only kanban card with a barcode
     * when isAllowBarcodeModel returns true for the current model
     *
     * @param {Node} area
     * @param {String} direction
     *
     * @returns {String/Boolean}
     */
    focusNextCard(area, direction) {
        const {isGrouped} = this.props.list;
        const closestCard = document.activeElement.closest(".o_kanban_record");
        if (!closestCard) {
            return;
        }
        const groups = isGrouped
            ? [...area.querySelectorAll(".o_kanban_group")]
            : [area];
        let cards = [...groups]
            .map((group) => [...group.querySelectorAll(".o_kanban_record")])
            .filter((group) => group.length);

        if (isAllowedBarcodeModel(this.props.list.resModel)) {
            cards = cards.map((group) => {
                const result = group.filter((card) => {
                    return (
                        card.querySelectorAll('button[name="action_barcode_scan"]')
                            .length > 0
                    );
                });
                return result;
            });
        }

        let iGroup = null;
        let iCard = null;
        for (iGroup = 0; iGroup < cards.length; iGroup++) {
            const i = cards[iGroup].indexOf(closestCard);
            if (i !== -1) {
                iCard = i;
                break;
            }
        }
        if (iCard === undefined) {
            iCard = 0;
            iGroup = 0;
        }
        // Find next card to focus
        const nextCard = this.getNextCard(direction, iCard, cards, iGroup, isGrouped);

        if (nextCard && nextCard instanceof HTMLElement) {
            nextCard.focus();
            return true;
        }
    },

    async openBarcodeScanner() {
        if (this.showMessageScanProductPackage) {
            const action = await this.ormService.call(
                "stock.picking",
                "action_barcode_scan",
                [false, false]
            );
            this.action.doAction(action);
        }
    },
});

KanbanRenderer.template = "stock_barcodes.BarcodeKanbanRenderer";
