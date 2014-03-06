# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

import os
import base64

from PIL import Image

from openerp.osv import fields, osv, orm
try:
    from reportlab.graphics.barcode import createBarcodeDrawing, \
            getCodes
except :
    print "ERROR IMPORTING REPORT LAB"


def _get_code(self, cr, uid, context=None):
    """get availble code """
    codes = [(r, r) for r in getCodes()]
    codes.append(('qrcode','QR'))
    return codes


class tr_barcode(orm.Model):
    """ Barcode Class """
    _name = "tr.barcode"
    _description = "Barcode"
    _rec_name = 'code'

    def _get_barcode2(self, cr, uid, ids, name, attr, context=None):
        res = {}
        barcodes = self.browse(cr, uid, ids, context=context)
        for barcode in barcodes:
            res[barcode.id] = barcode.code
        return res

    _columns = {
        'code': fields.char('Barcode',size=256),
        'code2': fields.function(_get_barcode2, method=True, string='Barcode2', type='char', size=256, store=True),
        'res_model':fields.char('Model',size=256),
        'res_id':fields.integer('Res Id'),
        'image': fields.binary('Data'),
        'width':fields.integer("Width",
                help="Leave Blank or 0(ZERO) for default size"),
        'hight':fields.integer("Hight",
                help="Leave Blank or 0(ZERO) for default size"),
        'hr_form':fields.boolean("Human Readable",
                help="To genrate Barcode In Human readable form"),
        'barcode_type':fields.selection(_get_code, 'Type'),
    }

    def get_image(self, value, width, hight, hr, code='QR'):
        """ genrating image for barcode """
        options = {}
        if width:options['width'] = width
        if hight:options['hight'] = hight
        if hr:options['humanReadable'] = hr
        options['quiet'] = False
        options['barWidth'] = 2
#        options['isoScale'] = 1
        if code not in ['QR','qrcode']:
            try:
                ret_val = createBarcodeDrawing(code, value=str(value), **options)
            except Exception, e:
                raise osv.except_osv('Error', e)
            ret_val.save(formats=['svg'], fnRoot='barcode', outDir='/tmp/')
            os.system('rsvg-convert %s -o %s' % ('/tmp/barcode.svg', '/tmp/barcode.png'))
            return base64.encodestring(open("/tmp/barcode.png","rb").read())
        else:
            ret_val = False
            from qrtools import QR
            qrCode = QR(data=value)
            qrCode.encode()
            return base64.encodestring(open(qrCode.filename,"rb").read())

    def generate_image(self, cr, uid, ids, context=None):
        "button function for genrating image """
        if not context:
            context = {}

        for self_obj in self.browse(cr, uid, ids, context=context):
            image = self.get_image(self_obj.code,
                        code=self_obj.barcode_type or 'qrcode',
                        width=self_obj.width, hight=self_obj.hight,
                        hr=self_obj.hr_form)
            self.write(cr, uid, self_obj.id,
                {'image':image},context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
