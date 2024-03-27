/** @odoo-module */
/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, "Allow display.controlPanel overriding", {
    setup() {
        this._super(...arguments);
        if (this.props.context.control_panel_hidden) {
            this.display.controlPanel = false;
        }
    },
});
