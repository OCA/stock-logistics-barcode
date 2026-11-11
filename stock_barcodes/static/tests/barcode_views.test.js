/* Copyright 2026 Tecnativa - Carlos Dauden
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {expect, test} from "@odoo/hoot";
import {press, queryOne} from "@odoo/hoot-dom";
import {animationFrame} from "@odoo/hoot-mock";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";
import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";
import "@stock_barcodes/views/kanban/kanban_view.esm";
import "@stock_barcodes/views/kanban/kanban_record.esm";
import "@stock_barcodes/views/views.esm";
import "@stock_barcodes/widgets/boolean_toggle.esm";

class BarcodeTest extends models.Model {
    _name = "barcode.test";
    name = fields.Char();
    manual_entry = fields.Boolean();
    show_form_scan = fields.Boolean();
    _records = [{id: 1, name: "Test", manual_entry: true, show_form_scan: false}];
}

class StockPicking extends models.Model {
    _name = "stock.picking";
    name = fields.Char();
    _records = [{id: 1, name: "Transfer"}];
}

defineMailModels();
defineModels([BarcodeTest, StockPicking]);

test("normal form buttons retain native hotkey attributes", async () => {
    onRpc("action_confirm", () => {
        expect.step("confirm");
        return false;
    });
    await mountView({
        type: "form",
        resModel: "barcode.test",
        resId: 1,
        arch: `<form><button name="action_confirm" type="object" string="Confirm" data-hotkey="v"/></form>`,
    });
    expect("button[name='action_confirm']").toHaveAttribute("data-hotkey", "v");
    await press("alt+v");
    await animationFrame();
    expect.verifySteps(["confirm"]);
});

test("manual entry stays visible when reopening the wizard", async () => {
    await mountView({
        type: "form",
        resModel: "barcode.test",
        resId: 1,
        arch: `<form>
            <field name="show_form_scan" invisible="1"/>
            <div class="oe_stock_barcordes_content">
                <div class="scan_fields"><field name="name"/></div>
            </div>
            <field name="manual_entry" widget="barcode_boolean_toggle"/>
        </form>`,
    });
    expect(".scan_fields").toBeVisible();
    await contains(".o_field_widget[name='manual_entry'] input").click();
    expect(".scan_fields").not.toBeVisible();
    await contains(".o_field_widget[name='manual_entry'] input").click();
    expect(".scan_fields").toBeVisible();
});

test("Enter on a transfer card opens its barcode action", async () => {
    onRpc("action_barcode_scan", ({args}) => {
        expect(args[0]).toEqual([1]);
        expect.step("scan transfer");
        return false;
    });
    await mountView({
        type: "kanban",
        resModel: "stock.picking",
        arch: `<kanban js_class="stock_barcodes_kanban"><templates><t t-name="card">
            <field name="name"/>
            <button type="object" name="action_barcode_scan" string="Scan"/>
        </t></templates></kanban>`,
    });
    queryOne(".o_kanban_record[data-id]").focus();
    await press("Enter");
    await animationFrame();
    expect.verifySteps(["scan transfer"]);
});

test("transfer scanning requires a concrete transfer", async () => {
    onRpc("action_barcode_scan", ({args}) => {
        expect(args[0]).toEqual([1]);
        expect.step("open scanner");
        return {type: "ir.actions.act_window_close"};
    });
    await mountView({
        type: "kanban",
        resModel: "stock.picking",
        arch: `<kanban js_class="stock_barcodes_kanban"><templates><t t-name="card">
            <field name="name"/>
            <button type="object" name="action_barcode_scan" string="Scan"/>
        </t></templates></kanban>`,
    });
    expect(".o_kanban_stock_barcodes").toHaveCount(0);
    await contains("button[name='action_barcode_scan']").click();
    expect.verifySteps(["open scanner"]);
});
