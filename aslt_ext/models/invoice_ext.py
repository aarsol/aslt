from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import datetime, date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re
import pdb


class account_payment(models.Model):
    _inherit = 'account.payment'

    payment_types = fields.Selection(related='journal_id.payment_types', selection=[
        ('paypall', 'Pay Pall'),
        ('cheque', 'Cheque'), ('Exchange_company', 'Exchange Company'), ('cross_settlement', 'Cross Settlement')
    ], string='Payment Type', tracking=True)
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, readonly=True,
                           states={'draft': [('readonly', False)]}, copy=False, tracking=True)

    journal_type = fields.Selection(related='journal_id.type', selection=[
        ('cash', 'Cash'),
        ('sale', 'Sale'), ('bank', 'Bank'), ('general', 'Miscellaneous'), ('purchase', 'Purchase')
    ], string='Payment Type', tracking=True)

    invoice_ref = fields.Char('Invoice Reference')
    bank_receipt = fields.Binary(string="Bank Receipt", attachment=True)

    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Date('Cheque Date')
    cross_vendor = fields.Many2one('res.partner', string='Vendor Name')
    cross_invoice = fields.Many2one('account.move', string='Invoice No')
    cross_amount = fields.Monetary(related='cross_invoice.amount_total', string='Invoice Amount')
    exchange_company_id = fields.Many2one('exchange.company', string='Exchange Company')
    receiver_name = fields.Char('Receiver Name')
    exchange_receipt_no = fields.Char('Receipt No')

    bank_deposit_due_date = fields.Date('Bank Deposit Due Date', compute='_compute_saturday', store=True)
    need_bank_deposit = fields.Boolean(default=False)

    def _compute_saturday(self):
        for rec in self:
            rec.bank_deposit_due_date = False
            if rec.journal_id.type == 'cash':
                today = date.today()
                rec.bank_deposit_due_date = today + timedelta((5 - today.weekday()) % 7)
                rec.need_bank_deposit = True
            # else:
            #     rec.need_bank_deposit = False

    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """

        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})
            if rec.journal_id.type == 'cash':
                for inv in rec.invoice_ids:
                    inv.update({'payment_state': 'cash_paid'})

            for inv in rec.invoice_ids:

                inv.update({'bank_deposit_due_date': self.bank_deposit_due_date})
                if self.amount != inv.amount_residual:
                    inv.update({'invoice_state': 'partial_paid', 'date': self.due_date})
                else:
                    inv.update({'invoice_state': 'full_paid'})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id) \
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids') \
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id) \
                    .reconcile()

        return True


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('partial_paid', 'Partial Paid'),
        ('full_paid', 'Full Paid'), ('not_paid', 'Not Paid'), ('cash_paid', 'Cash Paid')
    ], string='Invoice Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    payment_state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('bank_paid', 'Bank Paid'), ('cash_paid', 'Cash Paid'), ('done_paid', 'Done Paid')
    ], string='Payment Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    bank_deposit_due_date = fields.Date('Bank Deposit Due Date')

    marked_user_id = fields.Many2one('res.users', 'Sale Person')
    marked_duedate = fields.Date('Marked Due Date')

    # def _compute_saturday(self):
    #     for rec in self:
    #         today =date.today()
    #         rec.bank_deposit_due_date = today + timedelta((5 - today.weekday()) % 7)

    def write(self, values):
        if values.get('marked_user_id', False):
            if not values.get('marked_duedate', False):
                today = date.today()
                values['marked_duedate'] = today + timedelta(days=3)
        res = super(AccountMove, self).write(values)

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_(
                'You cannot create a move already in the posted state. Please create a draft move and post it after.'))

        vals_list = self._move_autocomplete_invoice_lines_create(vals_list)

        moves = super(AccountMove, self).create(vals_list)

        for move in moves:

            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.today():
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(_(
                    "You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date and move.is_invoice(include_receipts=True):
                move.invoice_date = fields.Date.context_today(self)
                move.with_context(check_move_validity=False)._onchange_invoice_date()

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (
                    move.line_ids.tax_ids or move.line_ids.tag_ids):
                move.date = move.company_id.tax_lock_date + timedelta(days=1)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in moves:
            if move.auto_post and move.date > fields.Date.today():
                raise UserError(_("This move is configured to be auto-posted on {}".format(
                    move.date.strftime(get_lang(self.env).date_format))))

            move.message_subscribe([p.id for p in [move.partner_id, move.commercial_partner_id] if
                                    p not in move.sudo().message_partner_ids])

            to_write = {'state': 'posted'}

            if move.name == '/':
                # Get the journal's sequence.
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_('Please define a sequence on your journal.'))

                # Consume a new number.
                to_write['name'] = sequence.next_by_id(sequence_date=move.date)

            move.write(to_write)

            # Compute 'ref' for 'out_invoice'.
            if move.type == 'out_invoice' and not move.invoice_payment_ref:
                to_write = {
                    'invoice_payment_ref': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
                move.write(to_write)

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

        for move in moves:
            if not move.partner_id: continue
            if move.type.startswith('out_'):
                move.partner_id._increase_rank('customer_rank')
            elif move.type.startswith('in_'):
                move.partner_id._increase_rank('supplier_rank')
            else:
                continue

        # Trigger 'action_invoice_paid' when the invoice is directly paid at its creation.
        moves.filtered(lambda move: move.is_invoice(include_receipts=True) and move.invoice_payment_state in (
            'paid', 'in_payment')).action_invoice_paid()
        return moves


class AccountPaymentweekly(models.Model):
    _name = 'account.weekly.payment'
    _description = 'Account Weekly Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'invoice_ref'

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    date = fields.Date('Date')
    amount = fields.Monetary(string="Amount",
                             currency_field='currency_id')
    invoice_ref = fields.Char('Invoice Reference')
    account_weekly_line_ids = fields.One2many('account.weekly.payment.line', 'account_weekly_id',
                                              string='Weekly Payment')
    bank_receipt = fields.Binary(string="Bank Receipt", attachment=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approve', 'approve')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    _sql_constraints = [('name_invoice_ref', 'UNIQUE (invoice_ref)', 'Bank Invoice Reference Must be unique.')]

    def action_approve(self):
        for rec in self:
            total_amount = 0
            for line in rec.account_weekly_line_ids:
                total_amount += line.amount
            if total_amount == rec.amount:

                for pay in rec.account_weekly_line_ids:
                    search_invoice = self.env['account.move'].search([('name', '=', pay.payment_id.communication)])
                    if search_invoice:
                        search_invoice.update({'payment_state': 'done_paid'})
                    else:
                        search_invoice = self.env['account.move'].search([('ref', '=', pay.payment_id.communication)])
                        if search_invoice:
                            search_invoice.update({'payment_state': 'done_paid'})
                    pay.payment_id.update({'invoice_ref': self.invoice_ref, 'bank_receipt': self.bank_receipt,
                                           'need_bank_deposit': False})
                # for inv in rec.account_weekly_line_ids:
                #     inv.move_id.update({'payment_state': 'done_paid'})
                #     search_payment = self.env['account.payment'].search([('communication', '=', inv.move_id.name)])
                #     for pay in search_payment:
                #         pay.update({'invoice_ref': self.invoice_ref, 'bank_receipt': self.bank_receipt})
                self.update({'state': 'approve'})
            else:
                raise UserError(_('Amount must be equal to sum of total Receipt Amount ! '))


class AccountPaymentweeklyLine(models.Model):
    _name = 'account.weekly.payment.line'
    _description = 'Account Weekly Payment Line'
    payment_id = fields.Many2one('account.payment', string='Payment Receipt No')
    amount = fields.Monetary(related='payment_id.amount', string='Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    account_weekly_id = fields.Many2one('account.weekly.payment', string='Weekly Payment')


class AccountExchangeCompany(models.Model):
    _name = 'exchange.company'

    name = fields.Char('Exchange Company', reqired=True)
    code = fields.Char('code')



