# © 2019 Wassim Ghannoum <wassim@mediaengagers.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo.tests import common
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class GS1Barcode(common.TransactionCase):
    def test_decode(self):
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
        barcode = PREFIX + '01' + gtin + '17'
        barcode += expiry + '10' + lot + GS + '3105' + weight
        result = self.decode(barcode, context={})
        assert len(result) == 4, "The barcode should decode to 4 AIs"
        assert result.get('01') == gtin, "The GTIN should be %s" % gtin
        expected_res_17 = '2014-05-31', "The expiry date should be 2014-05-31"
        assert result.get('17') == expected_res_17
        assert result.get('10') == lot, "The lot should be %s" % lot
        assert result.get('310') == 0.06385, "The weight should be %s" % weight
        # AI 311 (expiry date) - day 0 will be replaced with day 31
        expiry = '140515'
        # AI 11 (lot number, variable length)
        lot = 'B04059A'
        weight = '006385'
        barcode = PREFIX + '01' + gtin + '11'
        barcode += expiry + '11' + lot + GS + '11' + weight
        result = self.decode(barcode, context={})
        assert len(result) == 4, "The barcode should decode to 4 AIs"
        assert result.get('01') == gtin, "The GTIN should be %s" % gtin
        expected_res_17 = '2014-05-31', "The expiry date should be 2014-05-31"
        assert result.get('17') == expected_res_17
        assert result.get('10') == lot, "The lot should be %s" % lot
        assert result.get('310') == 0.06385, "The weight should be %s" % weight
        gtin = '03400933816759'
        # AI 17 (expiry date) - day 0 will be replaced with day 31
        expiry = '140522'
        # AI 10 (lot number, variable length)
        lot = 'B04059A'
        # AI 310 (Net Weight in Kg, 5 decimals)
        weight = '006385'
        barcode = PREFIX + '01' + gtin + '17'
        barcode += expiry + '10' + lot + GS + '3105' + weight
        result = self.decode(barcode)
        assert len(result) == 4, "The barcode should decode to 4 AIs"
        assert result.get('01') == gtin, "The GTIN should be %s" % gtin
        expected_res_17 = '2014-05-22', "The expiry date should be 2014-05-22"
        assert result.get('17') == expected_res_17
        assert result.get('10') == lot, "The lot should be %s" % lot
        assert result.get('310') == 0.06385, "The weight should be %s" % weight
        gtin = '03400933816759'
        barcode = PREFIX + '01' + gtin + '17'
        barcode += expiry + '10' + lot + GS + '3105' + weight + '0'
        try:
            result = self.decode(barcode, context={})
            raise AssertionError("should have raised")
        except ValidationError as exc:
            _logger.error(exc)
