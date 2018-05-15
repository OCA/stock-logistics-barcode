# -*- coding: utf-8 -*-
# Copyright 2012 Numérigraphe SARL. All Rights Reserved.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

# Make it easier to divide integers and get floating point results
from __future__ import division

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GS1Barcode(models.Model):
    """GS1-128/GS1-Datamatrix barcode decoder API and configuration"""
    _name = "gs1_barcode"
    _description = __doc__

    ai = fields.Char(
        string='Application Identifer',
        size=14,
        help='The standard Application Identifier (AI)',
        required=True,
        index=True)

    name = fields.Char(
        string='Description',
        size=64,
        required=True,
        index=1,
        translate=True)

    length_fixed = fields.Boolean(
        string='Fixed-length Data',
        help='Indicates whether the length of '
             'the data for this Application '
             'Identifier is fixed or not.',
        default=True)

    length_max = fields.Integer(
        string='Maximum Data Length',
        help='Maximum length of the data for this '
             'Application Identifier.',
        required=True,
        default=30)

    length_min = fields.Integer(
        string='Minimum Data Length',
        help='Minimum length of the data for '
             'this Application Identifier.')

    decimal = fields.Boolean(
        string='Decimal Indicator',
        help='Indicates whether a digit is expected '
             'before the data for this Application '
             'Identifier to indicate the position of '
             'the decimal point.',
        default=False)

    type = fields.Selection(
        selection=[('string', 'Any character string'),
                   ('numeric', 'Numeric value'),
                   ('date', 'Date')],
        string='Data Type',
        required=True,
        default='string')

    _sql_constraints = [
        ('ai_uniq', 'unique (ai)',
         'The Application Identifier must be unique!'),
    ]
    _order = 'ai'

    @api.model
    def decode(self, barcode_string):
        """
        Decode a GS1-128/GS1-Datamatrix string to dictionary of values with
        Application Identifiers as keys.
        Please note that the string MUST contain a <GS> character (group
        separator) after each variable-length value. <GS> is usually
        expected to be sent as ASCII character 29 but that may be configured
        per user.

        If the same Application Identifier is present several times in the
        string, only the its last value is returned.

        @type  barcode_string: string
        @param barcode_string: GS1-128/GS1-Datamatrix string  to decode
        @return:               A dictionary of values with Application
                               Identifiers as keys
        """

        # Prefix and Group Separator
        prefix = self.env.user.gs1_barcode_prefix or ''
        separator = self.env.user.gs1_barcode_separator or '\x1D'

        if not barcode_string.startswith(prefix):
            raise UserError(_('Could not decode barcode : '
                              'wrong prefix - the code should '
                              'start with "%s"') % prefix)

        # We are going to use lots of regular expressions to decode the string,
        # and they all boil down to the following templates:
        #  * regular expression template to match the AI code %s, to the group
        #    "ai". Must be formated with a string
        AI = r'(?P<ai>%s)'
        #  * regular expression template to match a fixed-length value of
        #    %d characters, to the group called "value".
        #    Must be formated with an integer.
        FIXED_LENGTH = r'(?P<value>.{%d})'
        # * regular expression to match a variable length value ending with
        #   a <GS> character, to the group called "value".
        #   Must be formated with a pair of integers.
        VARIABLE_LENGTH = r'(?P<value>[^' + separator + r']{%d,%d}' + \
                          separator + r'?)'
        #  * regular expression to match the position of the decimal separator
        #    after the AI code, to the group called "decimal".
        DECIMAL = r'(?P<decimal>\d)'

        # Make a dictionary of compiled regular expressions to decode the
        # string
        ai_regexps = {}
        value_regexps = {}
        types = {}
        for config in self.search([]):
            # Compile a regular expression to match the Application Identifier
            ai = config.ai
            ai_regexps[ai] = re.compile(AI % ai)
            # Compile a regular expression to match the data format
            if config.length_fixed:
                value_regexp = FIXED_LENGTH % config.length_max
            else:
                value_regexp = VARIABLE_LENGTH % (config.length_min,
                                                  config.length_max)
            if config.decimal:
                value_regexp = DECIMAL + value_regexp
            value_regexps[ai] = re.compile(value_regexp)
            # remember the data type
            types[ai] = config.type

        # Now let's decode the string, one Application Identifier at a time
        results = {}
        # Start searching from the first character after the prefix
        position = len(prefix)
        while position < len(barcode_string):
            # Search for a known Application Identifier
            for (ai, regexp) in ai_regexps.items():
                match = regexp.match(barcode_string, position)
                if match:
                    position += len(match.group('ai'))

                    # We found the Application Identifier, now decode the value
                    try:
                        groups = value_regexps[ai].match(
                            barcode_string, position).groupdict()
                    except AttributeError:
                        raise UserError(_(
                            'Could not decode barcode: '
                            'incorrect value for Application '
                            'Identifer "%s" at position %d') % (ai, position))

                    position += len(groups['value'])
                    results[ai] = groups['value'].replace(separator, '')
                    if types[ai] == 'numeric':
                        results[ai] = int(results[ai])
                        if 'decimal' in groups:
                            # Account for the decimal position
                            results[ai] = results[ai] / (
                                10 ** int(groups['decimal']))
                            position += len(groups['decimal'])
                    if types[ai] == 'date':
                        # Format the date
                        gs1_date_str = results[ai]
                        # Some barcodes are edited with a day of 0
                        # GS1 specs say we have to interpret it as last day
                        # of month
                        if gs1_date_str.endswith('00'):
                            gs1_date_str = gs1_date_str[:5] + '1'
                            date_dt = datetime.strptime(
                                gs1_date_str, '%y%m%d') +\
                                relativedelta(days=31)
                        else:
                            date_dt = datetime.strptime(gs1_date_str, '%y%m%d')
                        results[ai] = fields.Date.to_string(date_dt)

                    # We know we won't match another AI for now, move on
                    break
            else:
                # We couldn't find another valid AI in the rest of the code,
                # give up
                raise UserError(_('Could not decode barcode: '
                                  'unknown Application Identifier '
                                  'at position %d') % position)

        return results
