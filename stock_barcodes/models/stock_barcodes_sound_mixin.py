# models/barcode_sound_mixin.py
from odoo import api, models


class BarcodeSoundMixin(models.AbstractModel):
    _name = "barcode.sound.mixin"
    _description = "Helpers to notify OK/KO sounds via bus"

    @api.model
    def _channel_for_user(self, user):
        # Must match the client subscription: ["res.partner", partner_id]
        return ["res.partner", user.partner_id.id]

    @api.model
    def _notify_sound(self, users, *, event=None, sound_src=None):
        """Send a 'stock_barcodes.sound' bus message to given users.

        :param users: res.users recordset (or single)
        :param event: 'ok' or 'ko' (optional if sound_src provided)
        :param sound_src: absolute/asset URL to sound file
        """
        bus = self.env["bus.bus"].sudo()
        payload = {}
        if sound_src:
            payload["sound_src"] = sound_src
        elif event in ("ok", "ko"):
            payload["event"] = event
        else:
            return  # nothing to send

        for u in users:
            bus._sendone(self._channel_for_user(u), "stock_barcodes.sound", payload)

    # Shortcuts
    def sound_ok(self, users=None):
        self._notify_sound(users or self.env.user, event="ok")

    def sound_ko(self, users=None):
        self._notify_sound(users or self.env.user, event="ko")
