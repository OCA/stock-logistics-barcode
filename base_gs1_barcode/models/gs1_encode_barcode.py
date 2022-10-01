# Copyright 2021 Creu Blanca

from datetime import date, datetime

from odoo import _, exceptions, models


class GS1Barcode(models.AbstractModel):
    """GS1-128/GS1-Datamatrix barcode encoder function"""

    _name = "gs1.encode.barcode"
    _description = __doc__

    def encode_gs1(self):
        self.ensure_one()
        gs1_vals = self._encode_gs1_vals()
        result = ""
        gs1_barcode = self.env["gs1_barcode"]
        for key in gs1_vals:
            value = gs1_vals[key]
            if not value:
                continue
            ai = gs1_barcode.search([("ai", "=", key)])
            if not ai:
                continue
            result += key
            if ai.data_type == "date" and isinstance(value, date):
                value = value.strftime("%y%m%d000000")
            elif ai.data_type == "date" and isinstance(value, datetime):
                value = value.strftime("%y%m%d%H%M%S")
            elif ai.data_type == "numeric" and not ai.decimal:
                value = str(value).zfill(ai.length_max)
            elif ai.data_type == "numeric" and ai.decimal:
                raise NotImplementedError("Still on dev")
            value = str(value)[: ai.length_max]
            if len(value) < ai.length_min:
                raise exceptions.ValidationError(_("Size is not correct"),)
            result += value
            if len(value) < ai.length_max:
                result += "\x1D"
        return result

    def _encode_gs1_vals(self):
        """
        This must be implemented on each encoding object, it will return a
        dict with all the value
        :return: dict
        """
        return {}
