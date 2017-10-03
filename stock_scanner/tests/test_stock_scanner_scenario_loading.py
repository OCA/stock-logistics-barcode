# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import common
from odoo.tools.convert import convert_file
from ..load_scenario import get_xml_id


class TestStockScannerScenarioLoading(common.TransactionCase):
    def test_get_xml_id_from_id(self):
        """ Check the 'id' argument in get_xml_id """
        xml_id = get_xml_id('element', 'stock_scanner', {
            'id': 'the_id',
            # Add the two values in order to check the priority
            'reference_res_id': 'other_id',
        })
        self.assertEqual(xml_id, 'stock_scanner.the_id')

    def test_get_xml_id_from_reference_res_id(self):
        """ Check the 'id' argument in get_xml_id """
        xml_id = get_xml_id('element', 'stock_scanner', {
            'reference_res_id': 'other_id',
        })
        self.assertEqual(xml_id, 'stock_scanner.other_id')

    def test_get_xml_id_from_full_id(self):
        """ Check the 'id' argument in get_xml_id """
        xml_id = get_xml_id('element', 'stock_scanner', {
            'id': 'module_name.the_id',
            # Add the two values in order to check the priority
            'reference_res_id': 'other_id',
        })
        self.assertEqual(xml_id, 'module_name.the_id')

    def test_get_xml_id_from_full_reference_res_id(self):
        """ Check the 'id' argument in get_xml_id """
        xml_id = get_xml_id('element', 'stock_scanner', {
            'reference_res_id': 'module_name.other_id',
        })
        self.assertEqual(xml_id, 'module_name.other_id')

    def test_get_xml_id_without_value(self):
        """ Check the 'id' argument in get_xml_id """
        with self.assertRaises(exceptions.UserError):
            get_xml_id('element', 'stock_scanner', {})

    def test_wrong_model(self):
        """ Should raise if the model is not found """
        with self.assertRaises(ValueError):
            convert_file(
                self.env.cr, 'stock_scanner',
                'tests/data/TestWrongModel.scenario', {},
            )

    def test_wrong_company(self):
        """ Should raise if the company is not found """
        with self.assertRaises(ValueError):
            convert_file(
                self.env.cr, 'stock_scanner',
                'tests/data/TestWrongCompany.scenario', {},
            )

    def test_wrong_parent_scenario(self):
        """ Should raise if the parent scenario is not found """
        with self.assertRaises(ValueError):
            convert_file(
                self.env.cr, 'stock_scanner',
                'tests/data/TestWrongParent.scenario', {},
            )
