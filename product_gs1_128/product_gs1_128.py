# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2009 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""This file defines a utility class to encode/decode GS1-128 codes

GS1-128 codes (formerly known as UCC-128, EAN 128 or UCC/EAN-128) is a standard
for encoding item identification and logistics data.
Physically it is represented as a Code-128 bar-code, but this is not processed
here.
Instead we focus on decoding the data contained in this bar-code.
"""

# Make it easier to divide integers and get floating point results
from __future__ import division

import re
import time

import netsvc
from osv import osv, fields
from tools.translate import _

class invalid_gs1_128(osv.except_osv):
    """Indicate an error occurred while decoding a GS1-128 code"""
    pass

class product_gs1_128(osv.osv):
    """GS1-128 bar codes decoder configuration"""
    _name = "product.gs1_128"
    _description = __doc__
    _columns = {
        'ai' : fields.char('Application Identifer', size=14,
                           help='The standard Application Identifier (AI)',
                           required=1, select=1),
        'name': fields.char('Description', size=64, required=True, select=1,
                            translate=True),
        'length_fixed': fields.boolean('Fixed-length Data',
                                       help='Indicates whether the length of the data for this Application Identifier is fixed or not.'),
        'length_max': fields.integer('Maximum Data Length',
                                     help='Maximum length of the data for this Application Identifier.', required=1),
        'length_min': fields.integer('Minimum Data Length',
                                     help='Minimum length of the data for this Application Identifier.'),
        'decimal': fields.boolean('Decimal Indicator',
                                  help='Indicates whether a digit is expected before the data for this Application Identifier to indicate the position of the decimal point.'
                                  ),
        'type': fields.selection([ ('string', 'Any character string'),
                                    ('numeric', 'Numeric value'),
                                    ('date', 'Date') ],
                                    'Data Type', required=1),
    }
    _defaults = {
        'length_fixed': lambda * a: True,
        'length_max': lambda * a: 30,
        'decimal': lambda * a: False,
        'type': lambda * a: 'string',
    }
    _sql_constraints = [
        ('ai_uniq', 'unique (ai)', 'The Application Identifier must be unique!'),
    ]
    _order = 'ai'

    def decode(self, cr, uid, gs1_128_string, context=None):
        """
        Decode a GS1-128 string to dictionary of values with Application
        Identifiers as keys.
        Please note that the string MUST contain a <GS> character (group
        separator, ASCI code 29) after each variable-length value.
        
        If the same Application Identifier is present several times in the
        decoded, only the its last value is returned.
    
        @type  gs1_128_string: string
        @param gs1_128_string: GS1-128 string  to decode (ie. content of a code-128 bar code)
        @return:               A dictionary of values with Application Identifiers as keys
        """

        # Prefix and Group Separator
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        prefix = user.gs1_128_prefix or ''
        separator = user.gs1_128_separator or '\x1D'

        if not gs1_128_string.startswith(prefix):
            raise invalid_gs1_128(_('Error decoding GS1-128 code'),
                                 _('Could not decode GS1-128 code : wrong prefix - the code should start with "%s"') % prefix)

        # We are going to use lots of regular expressions to decode the string,
        # and they all boil down to the following templates:
        #  * regular expression template to match the AI code %s, to the group "ai". Must be formated with a string
        AI = r'(?P<ai>%s)'
        #  * regular expression template to match a fixed-length value of
        #    %d characters, to the group called "value".
        #    Must be formated with an integer.
        FIXED_LENGTH = r'(?P<value>.{%d})'
        # * regular expression to match a variable length value ending with
        #   a <GS> character, to the group called "value".
        #   Must be formated with a pair of integers.
        VARIABLE_LENGTH = r'(?P<value>[^' + separator + r']{%d,%d}' + separator + r'?)'
        #  * regular expression to match the position of the decimal separator
        #    after the AI code, to the group called "decimal".
        DECIMAL = r'(?P<decimal>\d)'

        # Make a dictionary of compiled regular expressions to decode the string
        ai_regexps = {}
        value_regexps = {}
        types = {}
        for config in self.browse(cr, uid,
                                  self.search(cr, uid, [], context=context),
                                  context=context):
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
        # start searching from the first character after the prefix
        position = len(prefix)
        while position < len(gs1_128_string):
            # Search for a known Application Identifier
            for (ai, regexp) in ai_regexps.items():
                match = regexp.match(gs1_128_string, position)
                if match:
                    position += len(match.group('ai'))

                    # We found the Application Identifier, now decode the value
                    try:
                        groups = value_regexps[ai].match(gs1_128_string, position).groupdict()
                    except AttributeError:
                        raise invalid_gs1_128(_('Error decoding GS1-128 code'),
                                             _('Could not decode GS1-128 code: incorrect value for Application Identifer "%s" at position %d') % (ai, position))

                    position += len(groups['value'])
                    results[ai] = groups['value'].replace(separator, '')
                    if types[ai] == 'numeric':
                        results[ai] = int(results[ai])
                        if 'decimal' in groups:
                        # account for the decimal position
                            results[ai] = results[ai] / (10 ** int(groups['decimal']))
                            position += len(groups['decimal'])
                    if types[ai] == 'date':
                        # format the date
                        results[ai] = time.strftime('%Y-%m-%d',
                                                    time.strptime(results[ai],
                                                                  '%y%m%d'))

                    # We know we won't match another AI for now, move on
                    break
            else:
                # We couldn't find another valid AI in the rest of the code, give up
                raise invalid_gs1_128(_('Error decoding GS1-128 code'),
                                      _('Could not decode GS1-128 code : unknown Application Identifier at position %d') % position)

        return results
