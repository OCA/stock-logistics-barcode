# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import subprocess
from subprocess import PIPE

from odoo import _, fields, models
from odoo.fields import first
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


class WizStockBarcodesReadMoveLocation(models.TransientModel):
    _name = "wiz.stock.barcodes.read.move.location"
    _inherit = "wiz.stock.barcodes.read"
    _description = "Wizard to read barcode on move location"

    move_location_id = fields.Many2one(
        comodel_name="wiz.stock.move.location", string="Move Location", readonly=True
    )
    move_location_qty = fields.Float(
        string="To Move quantities", digits="Product Unit of Measure", readonly=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location", string="Destination Location", readonly=True
    )

    def action_zbarcam(self):
        res = False
        proc = subprocess.Popen(["zbarcam"], stdout=PIPE, stderr=PIPE)
        (res, error) = proc.communicate()
        _logger.info(res)
        barcodes = str(res.decode("utf-8"))
        # TODO move to stock_barcodes_zbarcam module
        # TODO implement other barcodes types
        qr = find_between(barcodes, "QR-Code:", "\n")
        if qr:
            qr = qr.replace("}", "},")  # for multiple lectures
            qr = "[" + qr + "]"
            qr = safe_eval(qr)
            for bar in qr:
                self.barcode = str(bar)
                self.reset_qty()
                self.process_barcode(str(bar))
                self.action_manual_entry()
        code128 = find_between(barcodes, "CODE-128:", "\n")
        if code128:
            code128 = code128.split(",")
            for bar in code128:
                self.barcode = str(bar)
                self.reset_qty()
                self.process_barcode(str(bar))
                self.action_manual_entry()

    def name_get(self):
        return [
            (rec.id, "{} - {}".format(_("Barcode reader"), self.env.user.name))
            for rec in self
        ]

    def _prepare_move_location_line(self):

        search_args = [
            ("location_id", "=", self.move_location_id.origin_location_id.id),
            ("product_id", "=", self.product_id.id),
        ]
        if self.lot_id:
            search_args.append(("lot_id", "=", self.lot_id.id))
        else:
            search_args.append(("lot_id", "=", False))
        res = self.env["stock.quant"].read_group(search_args, ["quantity"], [])
        max_quantity = res[0]["quantity"]
        # Apply the putaway strategy
        move_location_dest_id = self.move_location_id.destination_location_id
        self.location_dest_id = (
            self.move_location_id.destination_location_id._get_putaway_strategy(
                self.product_id
            )
            or move_location_dest_id
        )
        return {
            "product_id": self.product_id.id,
            "origin_location_id": self.move_location_id.origin_location_id.id,
            "destination_location_id": self.location_dest_id.id,
            "product_uom_id": self.product_id.uom_id.id,
            "move_quantity": self.product_qty,
            "lot_id": self.lot_id.id,
            "max_quantity": max_quantity,
        }

    def _add_move_location_line(self):
        MoveLocationLine = self.env["wiz.stock.move.location.line"]
        line = self.move_location_id.stock_move_location_line_ids.filtered(
            lambda x: (x.product_id == self.product_id and x.lot_id == self.lot_id)
        )
        if line:
            line.write({"move_quantity": line.move_quantity + self.product_qty})
        else:
            line = MoveLocationLine.create(self._prepare_move_location_line())
            self.move_location_id.stock_move_location_line_ids = [(4, line.id)]

        self.move_location_qty = line.move_quantity

    def check_done_conditions(self):
        if self.product_id.tracking != "none" and not self.lot_id:
            self._set_messagge_info("info", _("Waiting for input lot"))
            return False

        force_add_log = self.env.context.get("force_add_log", False)
        if self.manual_entry and not force_add_log:
            return False
        return super().check_done_conditions()

    def action_done(self):
        if self.check_done_conditions() and self.env.context.get("manual_entry", False):
            result = super().action_done()
            if result:
                self._add_move_location_line()
            return result

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.with_context(force_add_log=True, manual_entry=True).action_done()
        return result

    def reset_qty(self):
        super().reset_qty()
        self.move_location_qty = 0.0

    def action_undo_last_scan(self):
        res = super().action_undo_last_scan()
        log_scan = first(
            self.scan_log_ids.filtered(lambda x: x.create_uid == self.env.user)
        )
        if log_scan:
            sml_line_ids = self.move_location_id.stock_move_location_line_ids
            move_location_line = sml_line_ids.filtered(
                lambda x: (
                    x.product_id == log_scan.product_id and x.lot_id == log_scan.lot_id
                )
            )
            if move_location_line:
                qty = move_location_line.move_quantity - log_scan.product_qty
                move_location_line.move_quantity = max(qty, 0.0)
                self.move_location_qty = move_location_line.move_quantity
        log_scan.unlink()
        return res
