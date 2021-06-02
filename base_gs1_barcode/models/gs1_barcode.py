# Copyright 2012-2014 Numérigraphe SARL.
# Make it easier to divide integers and get floating point results
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models


class GS1Barcode(models.Model):
    """GS1-128/GS1-Datamatrix barcode decoder API and configuration"""

    _name = "gs1_barcode"
    _description = __doc__
    _order = "ai"

    ai = fields.Char(
        "Application Identifier",
        size=14,
        required=True,
        help="The standard Application Identifier (AI)",
    )
    name = fields.Char("Description", required=True, translate=True)
    length_fixed = fields.Boolean(
        "Fixed-length Data",
        default=True,
        help=(
            "Indicates whether the length of the data "
            "for this Application Identifier is fixed or not."
        ),
    )
    length_max = fields.Integer(
        "Maximum Data Length",
        default=30,
        required=True,
        help="Maximum length of the data for this Application Identifier.",
    )
    length_min = fields.Integer(
        "Minimum Data Length",
        help="Minimum length of the data for this Application Identifier.",
    )
    decimal = fields.Boolean(
        "Decimal Indicator",
        help=(
            "Indicates whether a digit is expected before the data for this "
            "Application Identifier to indicate the position of the decimal "
            "point."
        ),
    )
    data_type = fields.Selection(
        [
            ("string", "Any character string"),
            ("numeric", "Numeric value"),
            ("date", "Date"),
        ],
        "Data Type",
        default="string",
        required=True,
    )

    _sql_constraints = [
        ("ai_uniq", "unique (ai)", "The Application Identifier must be unique!")
    ]

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
            genspecs/general-specifications_e_-section-3.pdf?sfvrsn=18,
            section 3.4.2, this denotes the end of the month.
            """
            if datestring.endswith("00"):
                date = (
                    datetime.strptime(datestring[:4], "%y%m")
                    + relativedelta(months=1)
                    - relativedelta(days=1)
                )
            else:
                date = datetime.strptime(datestring, "%y%m%d")
            return fields.Date.to_string(date)

        # Prefix and Group Separator
        # Search if the barcode contains the \x1D group separator already,
        # and then use it. Some scanners are able to pass this group separator,
        # and others are not able. If a user works with both devices,
        # this is becomes the most effective mechanism to ensure co-existence.
        if "\x1D" in barcode_string:
            separator = "\x1D"
        else:
            separator = self.env.user.gs1_barcode_separator or "\x1D"
        prefix = self.env.user.gs1_barcode_prefix or ""
        if not barcode_string.startswith(prefix):
            raise exceptions.ValidationError(
                _(
                    "Could not decode barcode : wrong prefix - the code should "
                    'start with "%s"'
                )
                % prefix
            )

        # We are going to use lots of regular expressions to decode the string,
        # and they all boil down to the following templates:
        #  * regular expression template to match the AI code %s, to the group
        #    "ai". Must be formated with a string
        AI = r"(?P<ai>%s)"
        #  * regular expression template to match a fixed-length value of
        #    %d characters, to the group called "value".
        #    Must be formated with an integer.
        #    <GS> can optionally follow after a fixed length value. See p.19
        #    of http://www.gs1.org/docs/barcodes/GS1_DataMatrix_Guideline.pdf
        FIXED_LENGTH = r"(?P<value>.{%d}" + separator + r"?)"
        # * regular expression to match a variable length value ending with
        #   a <GS> character, to the group called "value".
        #   Must be formated with a pair of integers.
        VARIABLE_LENGTH = r"(?P<value>[^" + separator + r"]{%d,%d}" + separator + r"?)"
        #  * regular expression to match the position of the decimal separator
        #    after the AI code, to the group called "decimal".
        DECIMAL = r"(?P<decimal>\d)"

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
                value_regexp = VARIABLE_LENGTH % (config.length_min, config.length_max)
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
            for (ai, regexp) in list(ai_regexps.items()):
                match = regexp.match(barcode_string, position)
                if not match:
                    continue
                position += len(match.group("ai"))

                # We found the Application Identifier, now decode the value
                try:
                    groups = (
                        value_regexps[ai].match(barcode_string, position).groupdict()
                    )
                except AttributeError:
                    raise exceptions.ValidationError(
                        _(
                            "Could not decode barcode: incorrect value for "
                            'Application Identifer "%s" at position %d'
                        )
                        % (ai, position)
                    )

                position += len(groups["value"])
                results[ai] = groups["value"].replace(separator, "").strip()
                if types[ai] == "numeric":
                    results[ai] = int(results[ai])
                    if "decimal" in groups:
                        # Account for the decimal position
                        results[ai] /= 10 ** int(groups["decimal"])
                        position += len(groups["decimal"])
                elif types[ai] == "date":
                    results[ai] = normalize_date(results[ai])

                # We know we won't match another AI for now, move on
                break
            else:
                # We couldn't find another valid AI in the rest of the code,
                # give up
                raise exceptions.ValidationError(
                    _(
                        "Could not decode barcode: unknown Application "
                        "Identifier at position %d"
                    )
                    % position
                )
        return results
