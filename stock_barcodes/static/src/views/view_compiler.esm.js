import {ViewCompiler} from "@web/views/view_compiler";
import {patch} from "@web/core/utils/patch";

/**
 * Ensure "data-hotkey" survives compilation onto the final <button>,
 * and optionally set native "accesskey" when it's a single character.
 * This keeps compatibility with UI overlays that read dataset.hotkey,
 * and with browsers that support access keys.
 */
patch(ViewCompiler.prototype, {
    compileButton(el, params) {
        // Read declared shortcuts from the source element
        const declaredHotkey =
            el.getAttribute("data-hotkey") ||
            el.getAttribute("data-shortcut") ||
            el.getAttribute("accesskey");

        // Clean source node before compiling to avoid duplication/side effects
        if (el.hasAttribute("data-hotkey")) {
            el.removeAttribute("data-hotkey");
        }
        if (el.hasAttribute("data-shortcut")) {
            el.removeAttribute("data-shortcut");
        }
        // Do not keep accesskey on the source node; we'll re-apply on the compiled button
        if (el.hasAttribute("accesskey")) {
            el.removeAttribute("accesskey");
        }

        // Compile the button with the original machinery
        const button = super.compileButton(el, params);

        // Re-apply attributes on the compiled button
        if (declaredHotkey) {
            // Keep data-hotkey so code relying on dataset.hotkey keeps working
            button.setAttribute("data-hotkey", declaredHotkey);

            // If it's a single character, also set native accesskey
            if (declaredHotkey.length === 1) {
                button.setAttribute("accesskey", declaredHotkey);
            }
        }

        return button;
    },
});
