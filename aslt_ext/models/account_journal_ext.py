from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re
import pdb


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_types = fields.Selection(selection=[
        ('paypall', 'Pay Pall'),
        ('cheque', 'Cheque'), ('Exchange_company', 'Exchange Company'), ('cross_settlement', 'Cross Settlement')
    ], string='Payment Type', tracking=True)