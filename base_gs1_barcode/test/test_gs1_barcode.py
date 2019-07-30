# © 2019 Wassim Ghannoum <wassim@mediaengagers.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo import exceptions
from odoo import _, fields
from odoo.tests import common


class GS1Barcode(common.TransactionCase):
    GS = '\x1D'
    PREFIX = ''
    # AI 01 (GTIN, fixed length)
    gtin = '03400933816759'
    # AI 17 (expiry date) - day 0 will be replaced with day 31
    expiry = '140500'
    # AI 10 (lot number, variable length)
    lot = 'B04059A'
    # AI 310 (Net Weight in Kg, 5 decimals)
    weight = '006385'
    
    barcode = PREFIX + '01' + gtin + '17' + expiry + '10' + lot + GS + '3105' + weight
    result = self.decode(barcode, context={})
    
    assert len(result)==4, "The barcode should decode to 4 AIs"
    assert result.get('01') == gtin, "The GTIN should be %s" % gtin
    assert result.get('17') == '2014-05-31', "The expiry date should be 2014-05-31"
    assert result.get('10') == lot, "The lot should be %s" % lot
    assert result.get('310') == 0.06385, "The weight should be %s" % weight

    
    gtin = '03400933816759'
    # AI 17 (expiry date) - day 0 will be replaced with day 31
    expiry = '140522'
    # AI 10 (lot number, variable length)
    lot = 'B04059A'
    # AI 310 (Net Weight in Kg, 5 decimals)
    weight = '006385'
    
    barcode = PREFIX + '01' + gtin + '17' + expiry + '10' + lot + GS + '3105' + weight
    result = self.decode(barcode, context={})
    
    assert len(result)==4, "The barcode should decode to 4 AIs"
    assert result.get('01') == gtin, "The GTIN should be %s" % gtin
    assert result.get('17') == '2014-05-22', "The expiry date should be 2014-05-22"
    assert result.get('10') == lot, "The lot should be %s" % lot
    assert result.get('310') == 0.06385, "The weight should be %s" % weight

    
    gtin = '03400933816759'
    barcode = PREFIX + '01' + gtin + '17' + expiry + '10' + lot + GS + '3105' + weight + '0'
    try:
        result = self.decode(barcode, context={})
        raise AssertionError("should have raised")
    except ValidationError as exc:
        print exc


