/** @odoo-module **/

/**
 * Alias of the standard Kanban view to be referenced via `js_class="stock_barcodes_kanban"`.
 * This lets us plug custom patches for Kanban (renderer/record/etc.) only where we opt-in.
 *
 * Usage in XML:
 *
 * <kanban js_class="stock_barcodes_kanban" ...>
 *   ...
 * </kanban>
 *
 * Notes:
 * - We explicitly keep `type: "kanban"` so the switcher and behaviors remain Kanban.
 * - If you later want to customize only some parts (Controller/Renderer/ArchParser),
 *   you can spread here and override those properties.
 */

import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

registry.category("views").add("stock_barcodes_kanban", {
    // Keep the base Kanban view config
    ...kanbanView,
    // Make sure type stays 'kanban' (explicit for clarity/future refactors)
    type: "kanban",
});
