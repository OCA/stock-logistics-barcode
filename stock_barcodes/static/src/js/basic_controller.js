/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes.BasicController", function (require) {
    "use strict";

    const BasicController = require("web.BasicController");
    const BrowserDetection = require("web.BrowserDetection");
    const BarcodesModelsMixin = require("stock_barcodes.BarcodesModelsMixin");
    const ui = require("@web/core/utils/ui");
    const getVisibleElements = ui.getVisibleElements;

    BasicController.include(BarcodesModelsMixin);
    BasicController.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this._is_valid_barcode_model = this._isAllowedBarcodeModel(
                this.initialState.model
            );
            if (this._is_valid_barcode_model) {
                this.BrowserDetection = new BrowserDetection();
                this._keybind_selectable_index = -1;
                this._keybind_selectable_items = [];
                this._is_browser_chrome = this.BrowserDetection.isBrowserChrome();
                const state_id = this.initialState.data.id;
                this._areAccessKeyVisible = false;
                if (state_id) {
                    this._channel_barcode_read = `stock_barcodes_read-${this.initialState.data.id}`;
                    this._channel_barcode_sound = `stock_barcodes_sound-${this.initialState.data.id}`;

                    if (this.call("bus_service", "isMasterTab")) {
                        this.call(
                            "bus_service",
                            "addChannel",
                            this._channel_barcode_read
                        );
                        this.call(
                            "bus_service",
                            "addChannel",
                            this._channel_barcode_sound
                        );
                    }
                }
            }
        },

        /**
         * @override
         */
        destroy: function () {
            this._super.apply(this, arguments);
            if (this._is_valid_barcode_model) {
                if (this.$sound_ok) {
                    this.$sound_ok.remove();
                }
                if (this.$sound_ko) {
                    this.$sound_ko.remove();
                }
            }
        },

        /**
         * @override
         */
        on_detach_callback: function () {
            this._super.apply(this, arguments);
            if (
                this._is_valid_barcode_model &&
                ["form", "kanban"].indexOf(this.initialState.viewType) !== -1
            ) {
                $(document).off("keydown", this._onDocumentKeyDown);
                $(document).off("keyup", this._onDocumentKeyUp);
                this.call(
                    "bus_service",
                    "off",
                    "notification",
                    this,
                    this.onBusNotificationBarcode
                );
            }
        },

        /**
         * @override
         */
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            if (
                this._is_valid_barcode_model &&
                ["form", "kanban"].indexOf(this.initialState.viewType) !== -1
            ) {
                this._appendBarcodesSounds();
                $(document).on("keydown", {controller: this}, this._onDocumentKeyDown);
                $(document).on("keyup", {controller: this}, this._onDocumentKeyUp);
                this.call(
                    "bus_service",
                    "on",
                    "notification",
                    this,
                    this.onBusNotificationBarcode
                );
                this._update_selectable_items();
            }
        },

        /**
         * Longpolling messages
         *
         * @param {Array} notifications
         */
        onBusNotificationBarcode: function (notifications) {
            for (const notif of notifications) {
                const [channel, message] = notif;
                if (channel === "stock_barcodes_read-" + this.initialState.data.id) {
                    if (message.action === "focus") {
                        setTimeout(() => {
                            this.$(`[name=${message.field_name}] input`).select();
                        }, 400);
                    }
                } else if (
                    channel ===
                    "stock_barcodes_sound-" + this.initialState.data.id
                ) {
                    if (message.sound === "ok") {
                        this.$sound_ok[0].play();
                    } else if (message.sound === "ko") {
                        this.$sound_ko[0].play();
                    }
                }
            }
        },

        _addHotkeyOverlays: function () {
            if (this._areAccessKeyVisible) {
                return;
            }
            for (const el of getVisibleElements(
                document,
                "[data-hotkey]:not(:disabled)"
            )) {
                const hotkey = el.dataset.hotkey;
                const overlay = document.createElement("div");
                overlay.className = "o_web_hotkey_overlay";
                overlay.appendChild(document.createTextNode(hotkey.toUpperCase()));

                let overlayParent = false;
                if (el.tagName.toUpperCase() === "INPUT") {
                    // Special case for the search input that has an access key
                    // defined. We cannot set the overlay on the input itself,
                    // only on its parent.
                    overlayParent = el.parentElement;
                } else {
                    overlayParent = el;
                }

                if (overlayParent.style.position !== "absolute") {
                    overlayParent.style.position = "relative";
                }
                overlayParent.appendChild(overlay);
            }
            this._areAccessKeyVisible = true;
        },

        _removeHotkeyOverlays: function () {
            if (!this._areAccessKeyVisible) {
                return;
            }
            for (const overlay of document.querySelectorAll(".o_web_hotkey_overlay")) {
                overlay.remove();
            }
            this._areAccessKeyVisible = false;
        },
        /**
         * Helper to toggle access keys panel visibility
         *
         * @param {Boolean} status
         */
        _toggleAccessKeys: function (status) {
            if (status) {
                this._addHotkeyOverlays();
            } else {
                this._removeHotkeyOverlays();
            }
        },

        /**
         * Used to manipulate fields
         *
         * @private
         */
        _postProcessFields: function () {
            // Set tabindex for readonly elements
            // this is necessary to don't block the elements chain
            const $fields = $("span.o_readonly_modifier");
            $fields.attr("tabindex", "-1");
        },

        /**
         * Append the audio elements to play the sounds.
         * This is here because only must exists one controller at time
         *
         * @private
         */
        _appendBarcodesSounds: function () {
            this.$sound_ok = $("<audio>", {
                src: "/stock_barcodes/static/src/sounds/bell.wav",
                preload: "auto",
            });
            this.$sound_ok.appendTo("body");
            this.$sound_ko = $("<audio>", {
                src: "/stock_barcodes/static/src/sounds/error.wav",
                preload: "auto",
            });
            this.$sound_ko.appendTo("body");
        },

        /**
         * Dedicated keyboard handle for chrome browser
         * @param {KeyboardEvent} ev
         */
        _onPushKeyForChrome: function (ev) {
            let prefixkey = "";
            if (ev.shift) {
                prefixkey += "shift+";
            }
            const elementWithAccessKey = document.querySelector(
                `[data-hotkey="${prefixkey}${ev.key.toLowerCase()}"], [data-hotkey="${prefixkey}${ev.key.toUpperCase()}"]`
            );
            if (elementWithAccessKey) {
                ev.preventDefault();
                elementWithAccessKey.focus();
                elementWithAccessKey.click();
            }
        },

        /**
         * @private
         * @param {KeyboardEvent} ev
         */
        _onDocumentKeyDown: function (ev) {
            var self = (ev.data && ev.data.controller) || this;
            if (self._is_valid_barcode_model) {
                // ACCESS KEY PANEL MANAGEMENT
                const alt = ev.altKey || ev.key === "Alt",
                    newEvent = _.extend({}, ev),
                    shift = ev.shiftKey || ev.key === "Shift";
                if (ev.keyCode === 113) {
                    // F2
                    self._toggleAccessKeys(!self._areAccessKeyVisible);
                } else if (self._areAccessKeyVisible && !shift && !alt) {
                    if (self._is_browser_chrome) {
                        self._onPushKeyForChrome(ev);
                    } else {
                        newEvent.altKey = true;
                        newEvent.shiftKey = true;
                        self._onKeyDown(newEvent);
                    }
                }
                // Open actions directly only when menu is active
                // 1-9 Only accesskey
                if (
                    self.initialState.data.display_menu &&
                    ((ev.keyCode >= 50 && ev.keyCode <= 57) ||
                        (ev.keyCode >= 97 && ev.keyCode <= 105))
                ) {
                    self.$(
                        "button[data-hotkey=" +
                            String.fromCharCode(ev.keyCode) +
                            "]:visible"
                    ).click();
                }

                // VIEW ACTIONS MANAGEMENT
                if (ev.keyCode === 120) {
                    // F9
                    self.$("button[name='action_clean_values']").click();
                } else if (ev.keyCode === 123 || ev.keyCode === 115) {
                    // F12  or F4
                    return self.open_action_menu();
                    // Self.$("button[name='open_actions']").click();
                } else if (ev.keyCode === $.ui.keyCode.UP) {
                    // Search kanban buttons to navigate
                    ev.preventDefault();
                    --self._keybind_selectable_index;
                    if (self._keybind_selectable_index < 0) {
                        self._keybind_selectable_index =
                            self._keybind_selectable_items.length - 1;
                    }
                    self._set_focus_on_selectable_item(
                        self._keybind_selectable_items,
                        self._keybind_selectable_index
                    );
                } else if (ev.keyCode === $.ui.keyCode.DOWN) {
                    ev.preventDefault();
                    ++self._keybind_selectable_index;
                    if (
                        self._keybind_selectable_index >=
                        self._keybind_selectable_items.length
                    ) {
                        self._keybind_selectable_index = 0;
                    }
                    self._set_focus_on_selectable_item(
                        self._keybind_selectable_items,
                        self._keybind_selectable_index
                    );
                } else if (ev.keyCode === $.ui.keyCode.ENTER || ev.keyCode === 13) {
                    if ($(".modal-dialog:visible").length) {
                        // Workaround: Bootstrap don't close modal when use 'enter' so, force click event.
                        const $button_confirm = $(".modal-footer .btn-primary:visible");
                        if ($button_confirm.length) {
                            $button_confirm.click();
                        }
                    } else {
                        // Try to click selectable item
                        const selectable_clicked = self._set_click_on_selectable_item(
                            self._keybind_selectable_items,
                            self._keybind_selectable_index
                        );
                        if (!selectable_clicked) {
                            // If not, try default validation buttons
                            // Only one button is visible
                            const $action_confirm = self.$(
                                "button[name='action_confirm']:visible"
                            );
                            const $action_confirm_force = self.$(
                                "button[name='action_force_done']:visible"
                            );
                            if ($action_confirm.length) {
                                $action_confirm.click();
                            } else if ($action_confirm_force.length) {
                                $action_confirm_force.click();
                            }
                        }
                    }
                }
            }
        },

        _set_focus_on_selectable_item: function (items, index) {
            if (items && index >= 0 && index < items.length) {
                items[index].focus();
                return true;
            }
            return false;
        },

        _set_click_on_selectable_item: function (items, index) {
            if (items && index >= 0 && index < items.length) {
                items[index].click();
                return true;
            }
            return false;
        },

        _update_selectable_items: function (reset_index) {
            if (reset_index) {
                this._keybind_selectable_index = -1;
            }
            this._keybind_selectable_items = this.$(
                ".oe_kanban_action_button:visible,.oe_btn_quick_action:visible"
            );
        },

        /**
         * @private
         * @param {KeyboardEvent} ev
         */
        _onDocumentKeyUp: function (ev) {
            var self = (ev.data && ev.data.controller) || this;
            if (self._is_valid_barcode_model) {
                if (
                    (!ev.altKey || ev.key !== "Alt") &&
                    !ev.ctrlKey &&
                    ev.keyCode !== 113
                ) {
                    self._toggleAccessKeys(false);
                }
            }
        },

        /* eslint-disable no-unused-vars */
        update: function (params, options) {
            return this._super.apply(this, arguments).then((res) => {
                this._update_selectable_items(true);
                return res;
            });
        },

        /**
         * @override
         */
        _applyChanges: function () {
            return this._super.apply(this, arguments).then((res) => {
                this._update_selectable_items();
                return res;
            });
        },

        open_action_menu: function () {
            return this.do_action("stock_barcodes.action_stock_barcodes_action", {
                name: "Barcode wizard menu",
                res_model: "wiz.stock.barcodes.read.picking",
                type: "ir.actions.act_window",
            });
        },
    });
});
