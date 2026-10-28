/* Copyright 2020 Therp BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, xml} from "@odoo/owl";
import {advanceTime, press} from "@odoo/hoot-dom";
import {expect, test} from "@odoo/hoot";
import {useBus, useService} from "@web/core/utils/hooks";
import {barcodeService} from "@barcodes/barcode_service";
import {mountWithCleanup} from "@web/../tests/web_test_helpers";

class BarcodeListener extends Component {
    static template = xml`<div class="o_barcode_multiline_test"/>`;
    static props = ["*"];

    setup() {
        const barcode = useService("barcode");
        useBus(barcode.bus, "barcode_scanned", (event) => {
            expect.step(event.detail.barcode);
        });
    }
}

async function scan(keys) {
    for (const key of keys) {
        await press(key);
    }
    await advanceTime(barcodeService.maxTimeBetweenKeysInMs + 10);
}

test.tags("desktop");

test("multiline barcode is dispatched once with embedded newline", async () => {
    await mountWithCleanup(BarcodeListener);
    await scan(["S", "K", "U", ":", "A", "1", "Enter", "S", "N", ":", "9", "2"]);
    expect.verifySteps(["SKU:A1\nSN:92"]);
});

test("single-line scanner suffix does not enter the barcode", async () => {
    await mountWithCleanup(BarcodeListener);
    await scan(["O", "C", "D", "S", "A", "V", "E", "Enter"]);
    expect.verifySteps(["OCDSAVE"]);
});

test("tabs and consecutive separators are kept inside barcode", async () => {
    await mountWithCleanup(BarcodeListener);
    await scan(["A", "B", "C", "Tab", "Tab", "D", "E", "F", "Enter"]);
    expect.verifySteps(["ABC\t\tDEF"]);
});

test("a scanner timeout splits distinct barcodes", async () => {
    await mountWithCleanup(BarcodeListener);
    await scan(["A", "A", "A", "Enter"]);
    await scan(["B", "B", "B", "Enter"]);
    expect.verifySteps(["AAA", "BBB"]);
});

test("first line can contain fewer than three characters", async () => {
    await mountWithCleanup(BarcodeListener);
    await scan(["A", "Enter", "B", "C", "D"]);
    expect.verifySteps(["A\nBCD"]);
});

test("a trailing Tab is ignored on a single-line barcode", async () => {
    await mountWithCleanup(BarcodeListener);
    await scan(["S", "I", "N", "G", "L", "E", "Tab"]);
    expect.verifySteps(["SINGLE"]);
});
