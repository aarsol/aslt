from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import pdb
import json


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_types = fields.Selection([('paypall', 'Pay Pall'),
                                      ('pos_machine', 'Pos Machine'),
                                      ('cheque', 'Cheque'),
                                      ('exchange_company', 'Exchange Company'),
                                      ('cross_settlement', 'Cross Settlement'),
                                      ('online_credit_card', 'Online Credit Card')
                                      ], string='Payment Type', tracking=True)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_types = fields.Selection(related='journal_id.payment_types', string='Payment Type',
                                     tracking=True)
    # selection = [('paypall', 'Pay Pall'),
    #              ('pos_machine', 'Pos Machine'),
    #              ('cheque', 'Cheque'),
    #              ('exchange_company',
    #               'Exchange Company'),
    #              ('cross_settlement',
    #               'Cross Settlement'),
    #              ('online_credit_card',
    #               'Online Credit Card')
    #              ],

    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, readonly=True,
                           states={'draft': [('readonly', False)]}, copy=False, tracking=True)
    journal_type = fields.Selection(related='journal_id.type', string='Journal Type', tracking=True)
    # , selection = [('cash', 'Cash'),
    #                ('sale', 'Sale'),
    #                ('bank', 'Bank'),
    #                ('general', 'Miscellaneous'),
    #                ('purchase', 'Purchase')
    #                ],

    invoice_ref = fields.Char('Invoice Reference')
    attachment_ids = fields.Many2many('ir.attachment', string='Files', help='Attachments for the Payments.')

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
    reference_cc = fields.Char('Reference No')

    note_salesman = fields.Char('Note By Salesmen')
    note_accountant = fields.Char('Note By Accountant')

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

            # if payment received from Customer
            if rec.payment_type == 'inbound':
                template = self.env.ref('aslt_ext.aslt_mail_template_data_payment_receipt')
                send = template.with_context(mail_create_nolog=True).send_mail(self.id, force_send=True)
        return True


class account_payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_types = fields.Selection(related='journal_id.payment_types', string='Payment Type')
    # selection = [('paypall', 'Pay Pall'),
    #              ('pos_machine', 'Pos Machine'),
    #              ('cheque', 'Cheque'),
    #              ('exchange_company',
    #               'Exchange Company'),
    #              ('cross_settlement',
    #               'Cross Settlement'),
    #              ('online_credit_card',
    #               'Online Credit Card')
    #              ],
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, readonly=True,
                           states={'draft': [('readonly', False)]}, copy=False)
    journal_type = fields.Selection(related='journal_id.type', string='Journal Type')
    # selection = [('cash', 'Cash'),
    #              ('sale', 'Sale'),
    #              ('bank', 'Bank'),
    #              ('general', 'Miscellaneous'),
    #              ('purchase', 'Purchase')
    #              ],

    invoice_ref = fields.Char('Invoice Reference')
    attachment_ids = fields.Many2many('ir.attachment', string='Files', help='Attachments for the Payments.')

    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Date('Cheque Date')

    # cross_vendor = fields.Many2one('res.partner', string='Vendor Name')
    # cross_invoice = fields.Many2one('account.move', string='Invoice No')
    # cross_amount = fields.Monetary(related='cross_invoice.amount_total', string='Invoice Amount')

    exchange_company_id = fields.Many2one('exchange.company', string='Exchange Company')
    receiver_name = fields.Char('Receiver Name')
    exchange_receipt_no = fields.Char('Receipt No')

    approval_code = fields.Char('Approval Code')
    transaction_id = fields.Char('Transaction ID')
    reference_cc = fields.Char('Reference No')

    note_salesman = fields.Char('Note By Salesmen')
    note_accountant = fields.Char('Note By Accountant')

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

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'invoice_ref': self.invoice_ref,
            'note_salesman': self.note_salesman,
            'note_accountant': self.note_accountant,
            'attachment_ids': self.attachment_ids,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'write_off_line_vals': [],
        }
        print(payment_vals, "Payment Vals from Wizard.")
        conversion_rate = self.env['res.currency']._get_conversion_rate(
            self.currency_id,
            self.company_id.currency_id,
            self.company_id,
            self.payment_date,
        )

        if self.payment_difference_handling == 'reconcile':

            if self.early_payment_discount_mode:
                epd_aml_values_list = []
                for aml in batch_result['lines']:
                    if aml._is_eligible_for_early_payment_discount(self.currency_id, self.payment_date):
                        epd_aml_values_list.append({
                            'aml': aml,
                            'amount_currency': -aml.amount_residual_currency,
                            'balance': aml.company_currency_id.round(-aml.amount_residual_currency * conversion_rate),
                        })

                open_amount_currency = self.payment_difference * (-1 if self.payment_type == 'outbound' else 1)
                open_balance = self.company_id.currency_id.round(open_amount_currency * conversion_rate)
                early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
                for aml_values_list in early_payment_values.values():
                    payment_vals['write_off_line_vals'] += aml_values_list

            elif not self.currency_id.is_zero(self.payment_difference):
                if self.payment_type == 'inbound':
                    # Receive money.
                    write_off_amount_currency = self.payment_difference
                else: # if self.payment_type == 'outbound':
                    # Send money.
                    write_off_amount_currency = -self.payment_difference

                write_off_balance = self.company_id.currency_id.round(write_off_amount_currency * conversion_rate)
                payment_vals['write_off_line_vals'].append({
                    'name': self.writeoff_label,
                    'account_id': self.writeoff_account_id.id,
                    'partner_id': self.partner_id.id,
                    'currency_id': self.currency_id.id,
                    'amount_currency': write_off_amount_currency,
                    'balance': write_off_balance,
                })
        return payment_vals


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_state = fields.Selection(selection=[('draft', 'Draft'),
                                                ('partial_paid', 'Partial Paid'),
                                                ('full_paid', 'Full Paid'),
                                                ('not_paid', 'Not Paid'),
                                                ('cash_paid', 'Cash Paid')
                                                ], string='Invoice Status', required=True, readonly=True, copy=False,
                                     default='draft')

    payment_state = fields.Selection(selection_add=[
        ('draft', 'Draft'),
        ('bank_paid', 'Bank Paid'),
        ('cash_paid', 'Cash Paid'),
        ('done_paid', 'Done Paid')
    ], ondelete={"draft": "set default"}, default='draft')
    # payment_state = fields.Selection(selection=[('draft', 'Draft'),
    #                                             ('bank_paid', 'Bank Paid'),
    #                                             ('cash_paid', 'Cash Paid'),
    #                                             ('done_paid', 'Done Paid')
    #                                             ], string='Payment Status', required=True, readonly=True, copy=False,
    #                                  tracking=True, default='draft')

    due_date = fields.Date('Due Date')
    completion_time = fields.Datetime('Completion Time')
    days_to_complete = fields.Integer('No of Days to Complete')
    bank_deposit_due_date = fields.Date('Bank Deposit Due Date')

    marked_user_id = fields.Many2one('res.users', 'Transferred Liability')
    marked_duedate = fields.Date('Liability Due Date')
    marked_state = fields.Selection(selection=[('draft', 'Draft'),
                                               ('accept', 'Accept'),
                                               ('cancel', 'Cancel')
                                               ], string='Liability Status', required=True, readonly=True, copy=False,
                                    tracking=True, default='draft')

    payment_count = fields.Integer(compute="_compute_payment_ids")
    shipment_company_id = fields.Many2one('shipment.company', string="Shipment Company")
    tracking_no = fields.Char('Tracking No')
    service_type = fields.Selection([('one_way', 'One Way'),
                                     ('written', 'Return')
                                     ], 'Service Type', default='one_way')
    invoice_rate = fields.Selection([('low', 'Low Rate'),
                                     ('high', 'High Rate')
                                     ], 'Invoice Rate', default='low')
    invoice_sale_id = fields.Many2one('account.move', 'Linked Sale Invoice')
    invoice_count = fields.Integer('Count', compute="_compute_inv_count", store=True)
    income_source = fields.Selection([('door_step', 'DoorStep'),
                                      ('walking', 'Walking'),
                                      ('web_mail', 'Web Mail')
                                      ], 'Income Source')

    # reference = fields.Char('Reference')
    bill_qty = fields.Float('Bill Qty', compute='_compute_bill_qty', store=True)
    bill_price_unit = fields.Float('Bill Price Unit', compute='_compute_bill_qty', store=True)

    def unlink(self):
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("Only Accounts Manager can delete the Entry"))
        return super(AccountMove, self).unlink()

    @api.depends('partner_id', 'partner_id.invoice_ids')
    def _compute_inv_count(self):
        for rec in self:
            rec.invoice_count = len(rec.partner_id.invoice_ids)

    def _compute_payment_ids(self):
        for rec in self:
            rec.payment_count = False
            search_payment = self.env['account.payment'].search([('invoice_ids', 'in', self.ids)])
            rec.payment_count = len(search_payment)

    def write(self, values):
        if values.get('marked_user_id', False):
            if not values.get('marked_duedate', False):
                today = date.today()
                values['marked_duedate'] = today + timedelta(days=3)

        res = super(AccountMove, self).write(values)

        if values.get('marked_user_id', False):
            template = self.env.ref('aslt_ext.email_template_invoice_transfer')
            send = template.with_context(mail_create_nolog=True).send_mail(self.id, force_send=True)

        # activity = self.env.ref('aslt_ext.mail_act_account_request_approval')
        # if not values.get('marked_user_id', False):
        #     raise UserError("You can't request an approval without Approver. (%s)" % self.marked_user_id)
        #
        # self.activity_schedule('aslt_ext.mail_act_account_request_approval',
        #                        user_id=values.get('marked_user_id', False))

        # Call the Email Sending Function
        if self.move_type == "out_invoice":
            if values.get('invoice_date', False):
                self.prepare_email_values(values)
        return res

    # @api.model_create_multi
    # def create(self, vals_list):
    #    move = super(AccountMove, self).create(vals_list)
    #    
    #    template = self.env.ref('aslt_ext.email_template_invoice')
    #    send = template.send_mail(move.id, force_send=True)
    #    move.post()
    #    return move

    def get_report_data(self):
        payment_data = json.loads(self.invoice_payments_widget or "{}")
        return payment_data['content'][0]

    @api.depends('invoice_line_ids', 'invoice_line_ids.quantity', 'invoice_line_ids.price_unit')
    def _compute_bill_qty(self):
        for rec in self:
            if rec.invoice_line_ids:
                line = rec.invoice_line_ids[0]
                rec.bill_qty = line.quantity
                rec.bill_price_unit = line.price_unit

    def prepare_email_values(self, values):
        mail_content = _(""" <p> Dear \n Following Modification Occur in the Invoiced</p> \n """)
        if values:
            i = 0
            for x, y in values.items():
                if not x == 'line_ids':
                    i += 1
                    mail_content += """ <b> %s:- </b> Value of Field <b><u>%s</u></b> is changed to <b><u>%s</u></b> <br/>""" % (
                        i, x, y)
        name = self.name
        if name == '/':
            name = self.partner_id.name

        main_content = {
            'subject': _('Modification In Invoice %s') % name,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': "payments@translationindubai.com",
            # 'email_to': "sarfraz_g2009@yahoo.com",
        }
        mail_id = self.env['mail.mail'].sudo().create(main_content)
        mail_id.send()


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
        moves.action_post()
        return moves

    def _get_partner_domain(self):
        if self.env.user.id < 3:
            domain = [('type', '=', 'invoice')]
        else:
            domain = [('type', '=', 'invoice'), '|', ('additional_user_ids', 'in', self.env.user.id),
                      ('user_id', '=', self.env.user.id)]
            # domain = ['|', '|',
            #     ('user_id', '=', self.env.user.id),
            #     '&', ('user_id', '=', False), ('branch_id', '=', self.env.user.branch_id.id),
            #     '&', ('user_id', '=', False), ('branch_id', '=', False)]

        partners = self.env['res.partner'].search(domain)
        partner_list = [x.id for x in partners]
        return partner_list

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        invoice = self._create_invoices(final=True)
        invoice.write({
            'income_source': self.income_source,
            'days_to_complete': self.days_to_complete,
        })
        return self.action_view_invoice()

    partner_list = fields.Many2many('res.partner', default=_get_partner_domain)
    shipment_company_id = fields.Many2one('shipment.company', string="Shipment Company")
    tracking_no = fields.Char('Tracking No')
    service_type = fields.Selection([('one_way', 'One Way'),
                                     ('written', 'Written')
                                     ], 'Service Type', default='one_way')

    completion_time = fields.Datetime('Completion Time')
    days_to_complete = fields.Integer('No of Days to Complete')
    city = fields.Char('City')
    income_source = fields.Selection([('door_step', 'DoorStep'),
                                      ('walking', 'Walking'),
                                      ('web_mail', 'Web Mail')
                                      ], 'Income Source')

    payment_methods = fields.Selection([('paypall', 'PayPall Link'),
                                        ('credit_card_link', 'Credit Card Link'),
                                        ('online_bank_transfer', 'Online Bank Transfer(Multiple)'),
                                        ('cash_deposit', 'Cash Deposit'),
                                        ('cash_over_counter', 'Cash Over The Counter'),
                                        ('cheque', 'Cheque'),
                                        ('card_swipe_machine', 'Card Swipe Machine'),
                                        ('exchange_company', 'Exchange Company')
                                        ], string='Payment Methods')

    @api.onchange('partner_id')
    def _onchange_partner_id_payment(self):
        self.payment_methods = self.partner_id.payment_methods

    @api.model
    def create(self, vals):
        template = False
        result = super(SaleOrder, self).create(vals)
        # result.send_quotation_create_email()
        template = self.env.ref('aslt_ext.aslt_mail_template_sale_quotation')
        if template:
            result.message_post_with_template(template.id, composition_mode='comment')
        return result

    def send_quotation_create_email(self):
        for rec in self:
            mail_content = _('New a Quotation <b> %s</b>, is Created at <b>%s</b> by the user <b>%s</b>.<br>') % \
                           (rec.name, self.create_date.strftime("%d-%m-%Y"), self.env.user.name)
            main_content = {
                'subject': _('Quotation %s Creation Alert') % rec.name,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': "info@translationindubai.com",
            }
            mail_id = self.env['mail.mail'].sudo().create(main_content)
            mail_id.send()

    @api.model
    def cron_24_hours(self):
        orders_list = []
        email_orders = False
        sale_orders = self.env['sale.order'].search([('state', '!=', 'cancel')])
        for order in sale_orders:
            invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.type in ('out_invoice', 'out_refund'))
            if not invoices:
                orders_list.append(order.id)
        email_orders = self.env['sale.order'].search([('id', 'in', orders_list)], order="create_date asc")
        if email_orders:
            mail_content = _(""" 
                            <table class='table table-bordered'> 
                                <tr>
                                    <th>Sr#</th>
                                    <th>Quotation</th>
                                    <th>Create Date</th>
                                    <th>Created By</th>
                                    <th>State</th>
                                    <th>Amount</th>
                                </tr>
                            """)
            sr = 0
            for email_order in email_orders:
                sr += 1
                mail_content += """
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>""" % (
                    sr, email_order.name, email_order.create_date.strftime("%d-%m-%Y"), email_order.create_uid.name,
                    email_order.state, email_order.amount_total)

            mail_content += """</table>"""

        main_content = {
            'subject': _('Non Invoices Quotations %s') % fields.Date.today().strftime('%d-%m-%Y'),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': "info@translationindubai.com",
        }
        mail_id = self.env['mail.mail'].sudo().create(main_content)
        mail_id.send()


class AccountPaymentweekly(models.Model):
    _name = 'account.weekly.payment'
    _description = 'Account Weekly Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'invoice_ref'

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    date = fields.Date('Date')
    amount = fields.Monetary(string="Amount", currency_field='currency_id')
    invoice_ref = fields.Char('Bank Deposit Slip No')
    journal_id = fields.Many2one('account.journal', 'Bank Journal')

    note_accountant = fields.Char('Note By Accountant')
    account_weekly_line_ids = fields.One2many('account.weekly.payment.line', 'account_weekly_id',
                                              string='Weekly Payment')
    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=1, help='Attachments for the Payments.')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('approve', 'approve')
                                        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
                             default='draft')

    _sql_constraints = [('name_invoice_ref', 'UNIQUE (invoice_ref)', 'Bank Deposit Slip No Must be unique.')]

    def action_approve(self):
        for rec in self:
            total_amount = 0
            for line in rec.account_weekly_line_ids:
                total_amount += line.amount

            if float_is_zero(total_amount - rec.amount, precision_rounding=1):
                for pay in rec.account_weekly_line_ids:
                    search_invoice = self.env['account.move'].sudo().search(
                        [('name', '=', pay.payment_id.communication)])
                    if search_invoice:
                        search_invoice.update({'payment_state': 'done_paid'})
                    else:
                        search_invoice = self.env['account.move'].sudo().search(
                            [('ref', '=', pay.payment_id.communication)])
                        if search_invoice:
                            search_invoice.update({'payment_state': 'done_paid'})
                    pay.payment_id.update({
                        'invoice_ref': rec.invoice_ref,
                        'attachment_ids': rec.attachment_ids,
                        'need_bank_deposit': False,
                        'note_accountant': rec.note_accountant,
                    })
                    if pay.payment_id.state == 'draft':
                        pay.payment_id.post()
                # for inv in rec.account_weekly_line_ids:
                #     inv.move_id.update({'payment_state': 'done_paid'})
                #     search_payment = self.env['account.payment'].search([('communication', '=', inv.move_id.name)])
                #     for pay in search_payment:
                #         pay.update({'invoice_ref': self.invoice_ref, 'attachment_ids': self.attachment_ids})
                self.update({'state': 'approve'})
                data = {
                    'payment_type': 'transfer',
                    'destination_journal_id': self.journal_id.id,
                    'state': 'draft',
                    'payment_method_id': 2,
                    'currency_id': 131,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'journal_id': 6,
                    'bank_deposit_due_date': False,
                    'need_bank_deposit': False,
                }
                payment = self.env['account.payment'].create(data)
                payment.post()
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
    _description = 'Exchange Company'

    name = fields.Char('Exchange Company', required=True)
    code = fields.Char('code')


class ShipmentCompany(models.Model):
    _name = 'shipment.company'
    _description = 'Shipment Company'

    name = fields.Char('Name', required=True)
    code = fields.Char('code')


class Partner(models.Model):
    _inherit = 'res.partner'

    payment_methods = fields.Selection([('paypall', 'PayPall Link'),
                                        ('credit_card_link', 'Credit Card Link'),
                                        ('online_bank_transfer', 'Online Bank Transfer(Multiple)'),
                                        ('cash_deposit', 'Cash Deposit'),
                                        ('cash_over_counter', 'Cash Over The Counter'),
                                        ('cheque', 'Cheque'),
                                        ('card_swipe_machine', 'Card Swipe Machine'),
                                        ('exchange_company', 'Exchange Company')
                                        ], string='Payment Methods')
    additional_user_ids = fields.Many2many('res.users', 'sale_person_id', string='Additional Sales Person')
    fax = fields.Char('Fax')
    type = fields.Selection(default='invoice')
    duplicated_bank_account_partners_count = fields.Integer(compute='_compute_duplicated_bank_account_partners_count')

    @api.depends('bank_ids')
    def _compute_duplicated_bank_account_partners_count(self):
        for partner in self:
            partner.duplicated_bank_account_partners_count = len(partner._get_duplicated_bank_accounts())

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_company', False):
                nme = vals.get('name', False)
                ids = self.env['res.partner'].sudo().search([('name', 'ilike', nme)])
                if ids:
                    raise Warning('Name already Exist')

        rec = super(Partner, self).create(vals_list)
        return rec


class User(models.Model):
    _inherit = 'res.users'

    def name_get(self):
        res = []
        for record in self.sudo():
            name = str(record.name) + ' - ' + str(record.branch_id.name)
            res.append((record.id, name))
        return res


class ResBranch(models.Model):
    _inherit = 'res.branch'

    other_details = fields.Html('Other Details')


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_company_details_empty = fields.Boolean()
