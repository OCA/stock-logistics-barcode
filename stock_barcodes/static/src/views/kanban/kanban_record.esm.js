/** @odoo-module */
/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {patch} from "@web/core/utils/patch";

patch(KanbanRecord.prototype, {
    async onGlobalClick(ev) {
        const record_barcode = $('div[name="inventory_quant_ids"]');
        if (record_barcode.length > 0) {
            const record = this.props.record;
            $("div.oe_kanban_operations").addClass("d-none");
            $("div.oe_kanban_operations-" + record.data.id).removeClass("d-none");
        }
        super.onGlobalClick(ev);
    },
});
