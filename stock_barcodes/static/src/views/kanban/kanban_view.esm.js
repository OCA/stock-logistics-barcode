/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

registry.category("views").add("stock_barcodes_kanban", {
    ...kanbanView,
});
