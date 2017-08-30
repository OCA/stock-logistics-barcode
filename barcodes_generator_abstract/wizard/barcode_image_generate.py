# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from io import BytesIO
import logging
logger = logging.getLogger(__name__)

try:
    import barcode
except ImportError:
    logger.debug('Cannot import barcode')


class BarcodeImageGenerate(models.TransientModel):
    _name = 'barcode.image.generate'
    _description = 'Wizard to generate a barcode image'

    @api.model
    def _supported_barcode_formats(self):
        res = []
        for barcode_format in barcode.PROVIDED_BARCODES:
            res.append((barcode_format, barcode_format))
        return res

    state = fields.Selection([
        ('config', 'config'),
        ('download', 'download'),
        ], default='config')
    image_format = fields.Selection([
        ('PNG', 'PNG'),
        ('JPEG', 'JPEG'),
        ], string='Image Format', default='PNG', required=True)
    # Idea for improvement: dynamically set the list of all supported
    # image formats from PIL ?
    dpi = fields.Integer(string='Image Size (DPI)', default=200, required=True)
    quiet_zone = fields.Float(
        string='Side Space', default=1.0,
        help="Size of the white space on the left and on the right of the "
             "barcode")
    write_text = fields.Boolean(
        string='Print Barcode Text', default=True,
        help="Print the text of the barcode under the image")
    text_distance = fields.Float(
        default=2.0,
        string='Space Between Barcode and Text',
        help="Size of the white space between the bottom of the barcode and "
             "the text of the barcode")
    module_height = fields.Float(
        default=15, string='Barcode Height',
        help="Vertical size of the barcode")
    module_width = fields.Float(
        default=0.2, string='Barcode Width',
        help="It doesn't seem to have any effect in EAN13...")
    font_size = fields.Integer(
        default=10, string='Font Size', help="Size of the text of the barcode")
    filename = fields.Char()
    # the 2 fields 'image' and 'image2' have the same value
    # 'image' is for the image widget, 'image2' is for the file widget
    image = fields.Binary(string='Barcode Image File', readonly=True)
    image2 = fields.Binary(string='Barcode Image File', readonly=True)
    barcode = fields.Char(string='Barcode', readonly=True, required=True)
    barcode_format = fields.Selection(
        '_supported_barcode_formats', string='Barcode Format', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(BarcodeImageGenerate, self).default_get(fields_list)
        if not res.get('barcode'):
            raise UserError(_('Barcode is not set on this form!'))
        if len(res['barcode']) == 13:
            res['barcode_format'] = 'ean13'
        elif len(res['barcode']) == 8:
            res['barcode_format'] = 'ean8'
        return res

    def generate(self):
        self.ensure_one()
        assert self.barcode, 'Missing barcode'
        assert self.barcode_format, 'Missing barcode format'
        imagewriter = barcode.writer.ImageWriter()
        imagewriter.format = self.image_format
        imagewriter.dpi = self.dpi
        barcode_obj = barcode.get(self.barcode_format, self.barcode)
        fullcode = barcode_obj.get_fullcode()
        if self.barcode != fullcode:
            raise UserError(_(
                "The Python Barcode library suggests that the "
                "full barcode corresponding to the format '%s' is %s "
                "(original barcode was %s).")
                % (self.barcode_format, fullcode, self.barcode))
        EAN = barcode.get_barcode_class(self.barcode_format)
        for field in [
                'quiet_zone', 'text_distance', 'write_text',
                'module_height', 'module_width', 'font_size']:
            EAN.default_writer_options[field] = self[field]
        ean = EAN(self.barcode, writer=imagewriter)
        fp = BytesIO()
        ean.write(fp)
        fp.seek(0)
        fname = _('barcode-%s-%s.%s') % (
            self.barcode_format, self.barcode, self.image_format.lower())
        image_b64 = fp.read().encode('base64')
        self.write({
            'image': image_b64,
            'image2': image_b64,
            'filename': fname,
            'state': 'download',
        })
        action = self.env['ir.actions.act_window'].for_xml_id(
            'barcodes_generator_abstract', 'barcode_image_generate_action')
        action['res_id'] = self.ids[0]
        return action

    def back2config(self):
        self.ensure_one()
        self.state = 'config'
        action = self.env['ir.actions.act_window'].for_xml_id(
            'barcodes_generator_abstract', 'barcode_image_generate_action')
        action['res_id'] = self.ids[0]
        return action
