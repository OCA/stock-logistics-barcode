/** @odoo-module **/
/* Copyright 2024 Tecnativa - Carlos Roca
/* Copyright 2024 Tecnativa - Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import { registry } from "@web/core/registry";
import {BooleanToggleField} from "@web/views/fields/boolean_toggle/boolean_toggle_field";

class FieldBarcodeBooleanToggleBig extends BooleanToggleField {}
FieldBarcodeBooleanToggleBig.template = "stock_barcodes_picking_batch_revision.FieldBarcodeBooleanToggleBig";

registry.category("fields").add("boolean_toggle_big", FieldBarcodeBooleanToggleBig);
