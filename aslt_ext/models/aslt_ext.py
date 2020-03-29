from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from datetime import datetime, date, timedelta
import pdb

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_types = fields.Selection([
        ('paypall', 'Pay Pall'),('pos_machine','Pos Machine'),
        ('cheque', 'Cheque'), ('exchange_company', 'Exchange Company'), ('cross_settlement', 'Cross Settlement')
    ], string='Payment Type', tracking=True)
    

class account_payment(models.Model):
    _inherit = 'account.payment'

    payment_types = fields.Selection(related='journal_id.payment_types', selection=[
        ('paypall', 'Pay Pall'),('pos_machine','Pos Machine'),
        ('cheque', 'Cheque'), ('exchange_company', 'Exchange Company'), ('cross_settlement', 'Cross Settlement')
    ], string='Payment Type', tracking=True)
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, readonly=True,
        states={'draft': [('readonly', False)]}, copy=False, tracking=True)

    journal_type = fields.Selection(related='journal_id.type', selection=[
        ('cash', 'Cash'), ('sale', 'Sale'), ('bank', 'Bank'), ('general', 'Miscellaneous'), ('purchase', 'Purchase')
    ], string='Journal Type', tracking=True)

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
    approval_code = fields.Char('Approval Code')
    transaction_id = fields.Char('Transaction ID')
    note_salesman = fields.Char('Note By Salesmen')
    note_accountant = fields.Char('Note By Accountant')
    attachment = fields.Binary(string="Attachment", attachment=True)

    bank_deposit_due_date = fields.Date('Bank Deposit Due Date', compute='_compute_saturday', store=True)
    need_bank_deposit = fields.Boolean(default=False)

    @api.depends('journal_id')
    def _compute_saturday(self):
        for rec in self:
            rec.bank_deposit_due_date = False
            if rec.journal_id.type == 'cash':
                today = date.today()
                rec.bank_deposit_due_date = today + timedelta((5 - today.weekday()) % 7)
                rec.need_bank_deposit = True
            # else:
            #     rec.need_bank_deposit = False

    def register_payment(self):        
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
            
            if rec.journal_id.type == 'cash':
                for inv in rec.invoice_ids:
                    inv.update({'payment_state': 'cash_paid'})

            for inv in rec.invoice_ids:
                inv.update(
                    {'bank_deposit_due_date': self.bank_deposit_due_date, 'invoice_payment_state': 'in_payment'})
                if self.amount != inv.amount_residual:
                    inv.update({'invoice_state': 'partial_paid', 'due_date': self.due_date})
                else:
                    inv.update({'invoice_state': 'full_paid'})

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

    due_date = fields.Date('Due Date')
    bank_deposit_due_date = fields.Date('Bank Deposit Due Date')

    marked_user_id = fields.Many2one('res.users', 'Marked SalesPerson')
    marked_duedate = fields.Date('Marked Due Date')
    marked_state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('accept', 'Accept'), ('cancel', 'Cancel')
    ], string='Marked Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    payment_count = fields.Integer(compute="_compute_payment_ids")
   

    def _compute_payment_ids(self):
        for rec in self:
            rec.payment_count = False
            search_payment = self.env['account.payment'].search([('invoice_ids','in',self.ids)])
            rec.payment_count = len(search_payment)

    def write(self, values):
        if values.get('marked_user_id', False):
            if not values.get('marked_duedate', False):
                today = date.today()
                values['marked_duedate'] = today + timedelta(days=3)
                
        res = super(AccountMove, self).write(values)        
                
        template = self.env.ref('aslt_ext.email_template_invoice_transfer')
        send = template.with_context(mail_create_nolog=True).send_mail(self.id, force_send=True)

                # activity = self.env.ref('aslt_ext.mail_act_account_request_approval')
                # if not values.get('marked_user_id', False):
                #     raise UserError("You can't request an approval without Approver. (%s)" % self.marked_user_id)
                #
                # self.activity_schedule('aslt_ext.mail_act_account_request_approval',
                #                        user_id=values.get('marked_user_id', False))
        return res
        

    #@api.model_create_multi
    #def create(self, vals_list):
    #    move = super(AccountMove, self).create(vals_list)
    #    
    #    template = self.env.ref('aslt_ext.email_template_invoice')
    #    send = template.send_mail(move.id, force_send=True)
    #    move.post()
    #    return move 
       
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        invoice.post()
        return invoice
        
        
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def _create_invoices(self, grouped=False, final=False):
        moves = super(SaleOrder, self)._create_invoices(grouped, final)
        moves.post()
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
    invoice_ref = fields.Char('Bank Deposit Slip No')
    account_weekly_line_ids = fields.One2many('account.weekly.payment.line', 'account_weekly_id',
                                              string='Weekly Payment')
    bank_receipt = fields.Binary(string="Bank Receipt", attachment=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approve', 'approve')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    _sql_constraints = [('name_invoice_ref', 'UNIQUE (invoice_ref)', 'Bank Deposit Slip No Must be unique.')]

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