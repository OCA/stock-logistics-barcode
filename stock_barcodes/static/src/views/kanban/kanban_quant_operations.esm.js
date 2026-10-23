/* @odoo-module */

/*
 * Inventory scan wizard: show the +1/-1 buttons of a quant card.
 * - Clicking a quant card shows its buttons and hides the others.
 * - stock.quant.enable_current_operations() sends a bus notification so the
 *   buttons stay visible once the kanban is reloaded after a +1/-1 click.
 * The quant kanban is an x2many, rendered by the core KanbanRenderer, so this
 * is done on the KanbanRecord.
 */

import {CANCEL_GLOBAL_CLICK, KanbanRecord} from "@web/views/kanban/kanban_record";
import {onMounted, onPatched, useEffect} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

const QUANTS_SELECTOR = "div[name='inventory_quant_ids']";

// Quant with visible operations. Kept outside the components because the
// records can be recreated when the kanban is reloaded.
let enabledQuantId = 0;

/** Show the operations of the given quant only, inside the container. */
export function showQuantOperations(container, quantId) {
    for (const el of container.querySelectorAll(".oe_kanban_operations")) {
        el.classList.toggle(
            "d-none",
            !el.classList.contains(`oe_kanban_operations-${quantId}`)
        );
    }
}

const _origSetup = KanbanRecord.prototype.setup;
const _origOnGlobalClick = KanbanRecord.prototype.onGlobalClick;

patch(KanbanRecord.prototype, {
    setup() {
        _origSetup.call(this, ...arguments);
        if (this.props.record.resModel !== "stock.quant") {
            return;
        }
        const busService = useService("bus_service");
        const refresh = () => {
            const container = this.rootRef.el?.closest(QUANTS_SELECTOR);
            if (container && enabledQuantId === this.props.record.resId) {
                showQuantOperations(container, enabledQuantId);
            }
        };
        const onKanbanUpdate = (notification) => {
            if (
                notification?.type === "enable_operations" &&
                notification.payload?.id === this.props.record.resId
            ) {
                enabledQuantId = notification.payload.id;
                refresh();
            }
        };
        onMounted(refresh);
        onPatched(refresh);
        useEffect(
            () => {
                busService.subscribe("stock_barcodes_kanban_update", onKanbanUpdate);
                return () =>
                    busService.unsubscribe(
                        "stock_barcodes_kanban_update",
                        onKanbanUpdate
                    );
            },
            () => []
        );
    },

    onGlobalClick(ev) {
        const container = this.rootRef.el?.closest(QUANTS_SELECTOR);
        if (
            container &&
            this.props.record.resModel === "stock.quant" &&
            !ev.target.closest(`${CANCEL_GLOBAL_CLICK},button`)
        ) {
            enabledQuantId = this.props.record.resId;
            showQuantOperations(container, enabledQuantId);
            return;
        }
        return _origOnGlobalClick.call(this, ...arguments);
    },
});
