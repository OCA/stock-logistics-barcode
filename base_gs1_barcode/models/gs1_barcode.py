# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2012-2014 Numérigraphe SARL.
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
##############################################################################

# Make it easier to divide integers and get floating point results
from __future__ import division

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.tools.translate import _
from openerp import models, fields, api, exceptions
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DATEFMT


class GS1Barcode(models.Model):
    """GS1-128/GS1-Datamatrix barcode decoder API and configuration"""
    _name = "gs1_barcode"
    _description = __doc__

    ai = fields.Char(
        'Application Identifier',
        size=14,
        required=True,
        help='The standard Application Identifier (AI)')
    name = fields.Char('Description', required=True, translate=True)
    length_fixed = fields.Boolean(
        'Fixed-length Data',
        default=True,
        help=('Indicates whether the length of the data '
              'for this Application Identifier is fixed or not.'))
    length_max = fields.Integer(
        'Maximum Data Length',
        default=30,
        required=True,
        help='Maximum length of the data for this Application Identifier.')
    length_min = fields.Integer(
        'Minimum Data Length',
        help='Minimum length of the data for this Application Identifier.')
    decimal = fields.Boolean(
        'Decimal Indicator',
        default=False,
        help=('Indicates whether a digit is expected before the data for this '
              'Application Identifier to indicate the position of the decimal '
              'point.'))
    data_type = fields.Selection(
        [('string', 'Any character string'), ('numeric', 'Numeric value'),
         ('date', 'Date')],
        'Data Type',
        default='string',
        required=True,
        oldname='type')

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
        @return: A dictionary of values with Application Identifiers as keys
        """

        def normalize_date(datestring):
            """
            Convert dates like '151231' as Odoo formatted '2015-12-31'.
            Note that the day can be underspecified as '00'. As per
            https://www.gs1.ch/docs/default-source/gs1-system-document/\
genspecs/general-specifications_e_-section-3.pdf?sfvrsn=18, section 3.4.2,
            this denotes the end of the month.
            """
            if datestring.endswith('00'):
                date = (datetime.strptime(datestring[:4], "%y%m") +
                        relativedelta(months=1) - relativedelta(days=1))
            else:
                date = datetime.strptime(datestring, '%y%m%d')
            return date.strftime(DATEFMT)

        # Prefix and Group Separator
        prefix = self.env.user.gs1_barcode_prefix or ''
        separator = self.env.user.gs1_barcode_separator or '\x1D'

        if not barcode_string.startswith(prefix):
            raise exceptions.ValidationError(
                _('Could not decode barcode : wrong prefix - the code should '
                  'start with "%s"') % prefix)

        # We are going to use lots of regular expressions to decode the string,
        # and they all boil down to the following templates:
        #  * regular expression template to match the AI code %s, to the group
        #    "ai". Must be formated with a string
        AI = r'(?P<ai>%s)'
        #  * regular expression template to match a fixed-length value of
        #    %d characters, to the group called "value".
        #    Must be formated with an integer.
        #    <GS> can optionally follow after a fixed length value. See p.19
        #    of http://www.gs1.org/docs/barcodes/GS1_DataMatrix_Guideline.pdf
        FIXED_LENGTH = r'(?P<value>.{%d}' + separator + r'?)'
        # * regular expression to match a variable length value ending with
        #   a <GS> character, to the group called "value".
        #   Must be formated with a pair of integers.
        VARIABLE_LENGTH = \
            r'(?P<value>[^' + separator + r']{%d,%d}' + separator + r'?)'
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
            types[ai] = config.data_type

        # Now let's decode the string, one Application Identifier at a time
        results = {}
        # Start searching from the first character after the prefix
        position = len(prefix)
        while position < len(barcode_string):
            # Search for a known Application Identifier
            for (ai, regexp) in ai_regexps.items():
                match = regexp.match(barcode_string, position)
                if not match:
                    continue
                position += len(match.group('ai'))

                # We found the Application Identifier, now decode the value
                try:
                    groups = value_regexps[ai].match(
                        barcode_string, position).groupdict()
                except AttributeError:
                    raise exceptions.ValidationError(
                        _('Could not decode barcode: incorrect value for '
                          'Application Identifer "%s" at position %d') % (
                            ai, position))

                position += len(groups['value'])
                results[ai] = groups['value'].replace(separator, '')
                if types[ai] == 'numeric':
                    results[ai] = int(results[ai])
                    if 'decimal' in groups:
                        # Account for the decimal position
                        results[ai] /= (10 ** int(groups['decimal']))
                        position += len(groups['decimal'])
                elif types[ai] == 'date':
                    results[ai] = normalize_date(results[ai])

                # We know we won't match another AI for now, move on
                break
            else:
                # We couldn't find another valid AI in the rest of the code,
                # give up
                raise exceptions.ValidationError(
                    _('Could not decode barcode: unknown Application '
                      'Identifier at position %d') % position)

        return results
