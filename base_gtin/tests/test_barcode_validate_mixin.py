# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from contextlib import contextmanager

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestBarcodeValidateAbstract(TransactionCase):

    def setUp(self):
        super(TestBarcodeValidateAbstract, self).setUp()

    @contextmanager
    def _test_record(self):
        model = self.env['barcode.validate.abstract']
        with mock.patch.multiple(
            model, _ids=mock.DEFAULT, _browse=mock.DEFAULT,
            env=mock.DEFAULT,
        ) as mk:
            rec_id = mock.MagicMock()
            mk['_ids'].__iter__.return_value = [rec_id.id]
            mk['_browse'].return_value = rec_id
            yield {
                'rec_ids': model,
                'rec_id': rec_id,
                'check_encoding':
                    mk['env']['barcode.nomenclature'].check_encoding,
            }

    def test_barcode_validate_valid(self):
        """ It should not raise error when valid barcode """
        with self._test_record() as mk:
            mk['check_encoding'].return_value = True
            mk['rec_ids']._barcode_validate('name')
            self.assertTrue(
                True,
                'This is a dummy assertion that will not be hit if fail',
            )

    def test_barcode_validate_invalid(self):
        """ It should raise error when invalid barcode """
        with self._test_record() as mk:
            mk['check_encoding'].return_value = False
            with self.assertRaises(ValidationError):
                mk['rec_ids']._barcode_validate('name')

    def test_barcode_validate_check_encoding(self):
        """ It should call check_encoding w/ proper args """
        with self._test_record() as mk:
            mk['rec_ids']._barcode_validate('name')
            mk['check_encoding'].assert_called_once_with(
                mk['rec_id'].name, mk['rec_id'].barcode_type,
            )
