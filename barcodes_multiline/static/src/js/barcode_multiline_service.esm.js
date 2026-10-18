/* Copyright 2020 Therp BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {barcodeService} from "@barcodes/barcode_service";
import {registry} from "@web/core/registry";
import {whenReady} from "@odoo/owl";

/**
 * Odoo 19's barcode service owns the keydown buffer in a private closure.
 * Instead of re-implementing that service, postpone Enter/Tab just long enough
 * to tell an embedded separator from the final scanner suffix.
 *
 * The service sees real keystrokes unmodified. When another character arrives
 * before its idle timeout, insert the pending separator as one synthetic
 * printable key. Without a following key, the normal barcode service emits the
 * pending barcode as-is when its own timeout expires.
 */
export const barcodeMultilineService = {
    dependencies: ["barcode"],
    start() {
        let lastKeyTime = 0;
        let hasBarcodeCharacters = false;
        let separator = null;
        let separatorTarget = null;
        const injected = new WeakSet();

        function isBarcodeTarget(target) {
            if (!(target instanceof Element)) {
                return false;
            }
            const editable = target.matches('input,textarea,[contenteditable="true"]');
            return (
                !editable ||
                target.classList.contains("o-barcode-input") ||
                Boolean(target.dataset.enableBarcode) ||
                target.getAttribute("barcode_events") === "true"
            );
        }

        function isBarcodeCharacter(event) {
            return (
                !event.metaKey &&
                (event.key?.length === 1 ||
                    event.key === "Alt" ||
                    event.key === "Control")
            );
        }

        function insertSeparator() {
            if (!separator || !separatorTarget?.isConnected) {
                return;
            }
            // Newline is a printable one-character key to Odoo's barcode service.
            // Dispatch from the scanner's target so the core service keeps the
            // target association (for barcode_events-enabled elements).
            const event = new KeyboardEvent("keydown", {
                key: separator,
                bubbles: true,
                cancelable: true,
            });
            injected.add(event);
            separatorTarget.dispatchEvent(event);
        }

        function onKeydown(event) {
            if (injected.has(event)) {
                return;
            }
            if (!isBarcodeTarget(event.target)) {
                hasBarcodeCharacters = false;
                separator = null;
                return;
            }
            const isTerminator = event.key === "Enter" || event.key === "Tab";
            const isCharacter = isBarcodeCharacter(event);
            if (!isTerminator && !isCharacter) {
                return;
            }

            const now = Date.now();
            const elapsed = now - lastKeyTime;
            // The scanner may pause between barcodes; never splice an old
            // separator into the next, distinct scan.
            if (elapsed > barcodeService.maxTimeBetweenKeysInMs) {
                hasBarcodeCharacters = false;
                separator = null;
            }

            if (isTerminator && hasBarcodeCharacters) {
                // Two consecutive delimiters means the first one was internal.
                if (separator) {
                    insertSeparator();
                }
                separator = event.key === "Enter" ? "\n" : "\t";
                separatorTarget = event.target;
                event.preventDefault();
                event.stopImmediatePropagation();
            } else if (isCharacter) {
                if (separator) {
                    insertSeparator();
                    separator = null;
                }
                hasBarcodeCharacters = true;
            }
            lastKeyTime = now;
        }

        whenReady(() => {
            document.body.addEventListener("keydown", onKeydown, true);
        });
    },
};

registry.category("services").add("barcodes_multiline", barcodeMultilineService);
