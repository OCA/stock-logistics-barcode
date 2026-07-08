/* Copyright 2024 Akretion
/* Copyright 2024 Tecnativa
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {getVisibleElements, isVisible} from "@web/core/utils/ui";
import {FormController} from "@web/views/form/form_controller";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {ListController} from "@web/views/list/list_controller";
import {_t} from "@web/core/l10n/translation";
import {isAllowedBarcodeModel} from "../utils/barcodes_models_utils.esm";
import {patch} from "@web/core/utils/patch";
import {useEffect} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {waitVisibleElement} from "../utils/wait_visible_elment_helper.esm";

let barcodeOverlaysVisible = false;

// This is necessary because the hotkey service does not make its API public for
// some reasons
export function barcodeRemoveHotkeyOverlays() {
    for (const overlay of document.querySelectorAll(".o_barcode_web_hotkey_overlay")) {
        overlay.remove();
    }
    barcodeOverlaysVisible = false;
}

// This is necessary because the hotkey service does not make its API public for
// some reasons
export function barcodeAddHotkeyOverlays(activeElement) {
    for (const el of getVisibleElements(
        activeElement,
        "[data-hotkey]:not(:disabled)"
    )) {
        const hotkey = el.dataset.hotkey;
        const overlay = document.createElement("div");
        overlay.classList.add(
            "o_barcode_web_hotkey_overlay",
            "position-absolute",
            "top-0",
            "bottom-0",
            "start-0",
            "end-0",
            "d-flex",
            "justify-content-center",
            "align-items-center",
            "m-0",
            "bg-black-50",
            "h6"
        );
        const overlayKbd = document.createElement("kbd");
        overlayKbd.className = "small";
        overlayKbd.appendChild(document.createTextNode(hotkey.toUpperCase()));
        overlay.appendChild(overlayKbd);

        let overlayParent = null;
        if (el.tagName.toUpperCase() === "INPUT") {
            // Special case for the search input that has an access key
            // defined. We cannot set the overlay on the input itself,
            // only on its parent.
            overlayParent = el.parentElement;
        } else {
            overlayParent = el;
        }

        if (overlayParent.style.position !== "absolute") {
            overlayParent.style.position = "relative";
        }
        overlayParent.appendChild(overlay);
    }
    barcodeOverlaysVisible = true;
}

function setupView() {
    const actionService = useService("action");
    const uiService = useService("ui");
    const busService = useService("bus_service");
    const notification = useService("notification");

    const handleKeys = async (ev) => {
        if (ev.keyCode === 113) {
            // F2
            const {activeElement} = uiService;

            if (barcodeOverlaysVisible) {
                barcodeRemoveHotkeyOverlays();
            } else {
                barcodeAddHotkeyOverlays(activeElement);
            }
        } else if (ev.keyCode === 120) {
            // F9
            const button = document.querySelector("button[name='action_clean_values']");
            if (isVisible(button)) {
                button.click();
            }
        } else if (ev.keyCode === 123 || ev.keyCode === 115) {
            // F12 or F4
            await actionService.doAction(
                "stock_barcodes.action_stock_barcodes_action_client",
                {
                    name: "Barcode wizard menu",
                    res_model: "wiz.stock.barcodes.read.picking",
                    type: "ir.actions.act_window",
                }
            );
        }
    };

    // Helpers: safe audio playback and idle callback fallback
    const safePlay = (audio) => {
        if (!audio) return;
        audio.play();
    };

    const handleNotification = (notif) => {
        const {payload, type} = notif;
        if (
            (this.model.root.resModel == payload.res_model) &
            (this.model.root.resId == payload.res_id)
        ) {
            if (type === "stock_barcodes_sound") {
                if (payload?.sound === "ko") {
                    safePlay(this.soundKo);
                } else {
                    safePlay(this.soundOk);
                }
            } else if (type === "stock_barcodes_focus") {
                requestIdleCallback(() => {
                    // Build a robust selector: [name="..."] input
                    let selector = "";
                    if (window.CSS && typeof CSS.escape === "function") {
                        selector = `[name="${CSS.escape(payload.field_name)}"] input`;
                    } else {
                        // Basic fallback (works si no hay caracteres especiales)
                        selector = `[name="${payload.field_name}"] input`;
                    }
                    setTimeout(() => {
                        waitVisibleElement(selector, 5000)
                            .then((input) => {
                                input.focus();
                                input.select();
                            })
                            .catch((err) => console.warn(err.message));
                    }, 300);
                });
            } else if (type === "stock_barcodes_notify") {
                notification.add(payload?.message || "", {
                    title: payload?.title,
                    type: payload?.type,
                    sticky: Boolean(payload?.sticky),
                });
            }
        }

        // Global (no limitados al record actual)
        if (type === "stock_barcodes_edit_manual") {
            if (payload?.manual_entry) {
                this.env.bus.trigger("enableFormEditBarcode");
            } else {
                this.env.bus.trigger("disableFormEditBarcode");
            }
        } else if (type === "actions_barcode") {
            if (payload?.valid_picking) {
                notification.add(_t("The transfer has been validated"), {
                    type: "success",
                });
            } else if (payload?.apply_inventory) {
                actionService.doAction(
                    "stock_barcodes.action_stock_barcodes_action_client"
                );
                notification.add(_t("The inventory adjustment has been validated"), {
                    type: "success",
                });
            }
        } else if (type === "actions_barcode_notification") {
            notification.add(_t(payload?.message || ""), {
                type: payload?.message_type,
                sticky: Boolean(payload?.sticky),
            });
        } else if (type === "count_apply_inventory") {
            // Restored from 16.0 (form_controller.esm.js, lost in the v18
            // migration): the backend sends the number of inventory quants
            // pending to apply on the "stock_barcodes_form_update" channel.
            // Write it into the Apply button counter span(s); without this the
            // span stayed empty and the button rendered "Apply ()".
            const count = payload?.count ?? "";
            document
                .querySelectorAll("span.count_apply_inventory")
                .forEach((el) => (el.textContent = count));
        }
    };

    // The bus service maps subscriptions by callback identity, so the same
    // function must never be subscribed to two notification types: the
    // second subscribe would overwrite the stored wrapper and unsubscribe
    // would leak the first listener, showing every notification once per
    // leaked handler.
    const handleFormUpdateNotification = (notif) => handleNotification(notif);

    useEffect(
        () => {
            // Keydown handler
            const onKeyDown = handleKeys;

            // Create audio elements without jQuery
            // (not needed to append to DOM to play)
            const soundOk = new Audio("/stock_barcodes/static/src/sounds/bell.wav");
            soundOk.preload = "auto";
            const soundKo = new Audio("/stock_barcodes/static/src/sounds/error.wav");
            soundKo.preload = "auto";

            // Store references on the component instance
            this.soundOk = soundOk;
            this.soundKo = soundKo;

            busService.subscribe("stock_barcodes_scan", handleNotification);
            // Inventory "Apply" button counter is pushed on this channel
            busService.subscribe(
                "stock_barcodes_form_update",
                handleFormUpdateNotification
            );
            // DOM event
            document.body.addEventListener("keydown", onKeyDown);

            // Cleanup
            return () => {
                busService.unsubscribe("stock_barcodes_scan", handleNotification);
                busService.unsubscribe(
                    "stock_barcodes_form_update",
                    handleFormUpdateNotification
                );
                document.body.removeEventListener("keydown", onKeyDown);
                // Drop references (not appended, so no DOM removal needed)
                this.soundOk = null;
                this.soundKo = null;
            };
        },
        // Subscribe once on mount: OWL default dependencies ([NaN]) re-apply
        // the effect on every render
        () => []
    );
}

function patchControllerSetup(Controller) {
    patch(Controller.prototype, {
        setup() {
            super.setup(...arguments);
            // Guard por si props aún no están listas
            const resModel = this?.props?.resModel;
            if (resModel && isAllowedBarcodeModel(resModel)) {
                // Ejecuta tu wiring (useEffect, bus, etc.)
                setupView.call(this);
            }
        },
    });
}
patchControllerSetup(KanbanController);
patchControllerSetup(FormController);
patchControllerSetup(ListController);
