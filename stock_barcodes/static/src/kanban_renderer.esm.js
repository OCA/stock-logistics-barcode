/** @odoo-module */
/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {isAllowedBarcodeModel} from "./barcodes_models_utils.esm";
import {patch} from "@web/core/utils/patch";
import {useBus} from "@web/core/utils/hooks";
import {useHotkey} from "@web/core/hotkeys/hotkey_hook";
import {useRef} from "@odoo/owl";

patch(KanbanRenderer.prototype, "add hotkey", {
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
    },
    // eslint-disable-next-line complexity
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

        if (nextCard && nextCard instanceof HTMLElement) {
            nextCard.focus();
            return true;
        }
    },
});

// Class BarcodeKanbanController extends KanbanController {
//     setup() {
//         super.setup();
//         this._appendBarcodesSounds();
//     }
//
//     /**
//      * Append the audio elements to play the sounds.
//      * This is here because only must exists one controller at time
//      *
//      * @private
//      */
//     _appendBarcodesSounds() {
//         this.$sound_ok = $("<audio>", {
//             src: "/stock_barcodes/static/src/sounds/bell.wav",
//             preload: "auto",
//         });
//         this.$sound_ok.appendTo("body");
//         this.$sound_ko = $("<audio>", {
//             src: "/stock_barcodes/static/src/sounds/error.wav",
//             preload: "auto",
//         });
//         this.$sound_ko.appendTo("body");
//     }
//
// }
