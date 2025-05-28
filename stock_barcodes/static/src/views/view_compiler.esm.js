/** @odoo-module */

import {ViewCompiler} from "@web/views/view_compiler";
import {patch} from "@web/core/utils/patch";

patch(ViewCompiler.prototype, {
    compileButton(el, params) {
        const hotkey = el.getAttribute("data-hotkey");
        el.removeAttribute("data-hotkey");
        const button = super.compileButton(el, params);
        if (hotkey) {
            button.setAttribute("hotkey", hotkey);
        }
        return button;
    },
});
