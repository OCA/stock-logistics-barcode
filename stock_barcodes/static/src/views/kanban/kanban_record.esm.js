/* @odoo-module */

/*
 * KanbanRecord Enter-key activation for Odoo 18 (compatible with 16/17).
 * - Enter en una .o_kanban_record dispara la acción primaria.
 * - Evita inputs/textarea/select/contenteditable.
 * - Añade tabindex/role si faltan (a11y).
 * - Limpia listeners al desmontar.
 */

import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {isVisible} from "@web/core/utils/ui";
import {patch} from "@web/core/utils/patch";
import {useEffect} from "@odoo/owl";

/** Return the first visible element matching the selector within root. */
function qVisible(root, selector) {
    const els = root.querySelectorAll(selector);
    for (const el of els) {
        if (el instanceof HTMLElement && isVisible(el)) {
            return el;
        }
    }
    return null;
}

/** Find the primary clickable target inside a kanban record. */
function resolvePrimaryTarget(recordEl) {
    return (
        qVisible(recordEl, ".oe_kanban_action_button, .oe_btn_quick_action") ||
        qVisible(recordEl, ".oe_kanban_global_click") ||
        qVisible(recordEl, "a, button")
    );
}

/** True if the event target is an editable field where Enter should not trigger actions. */
function isEditableTarget(target) {
    if (!target) return false;
    const tag = target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
    if (target.isContentEditable) return true;
    const editable = target.closest("[contenteditable=''],[contenteditable='true']");
    return Boolean(editable);
}

// Keep original setup to avoid using `super` in a patch
const _origSetup = KanbanRecord.prototype.setup;

patch(KanbanRecord.prototype, {
    setup() {
        if (typeof _origSetup === "function") {
            _origSetup.call(this, ...arguments);
        }

        useEffect(
            () => {
                const el = this.el;
                if (!(el instanceof HTMLElement)) {
                    // No cleanup needed
                    return;
                }

                // Ensure keyboard focusability / a11y if template didn't provide it.
                if (!el.hasAttribute("tabindex")) {
                    el.setAttribute("tabindex", "0");
                }
                if (!el.hasAttribute("role")) {
                    el.setAttribute("role", "button");
                }

                const onKeyDown = (ev) => {
                    if (ev.key !== "Enter") return;
                    if (!el.contains(ev.target)) return;
                    if (isEditableTarget(ev.target)) return;

                    // Avoid modified Enter (Ctrl/Meta/Shift/Alt)
                    if (ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) return;

                    const target = resolvePrimaryTarget(el);
                    if (target instanceof HTMLElement) {
                        target.click();
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                };

                // Capture phase to pre-empt other handlers
                el.addEventListener("keydown", onKeyDown, true);

                return () => {
                    el.removeEventListener("keydown", onKeyDown, true);
                };
            },
            () => []
        );
    },
});
