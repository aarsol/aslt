from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ResBranch(models.Model):
    _name = 'res.branch'
    _description = 'Branch'

    def copy(self, default=None):
        raise UserError(_('Duplicating a company is not allowed. Please create a new company instead.'))

    @api.model
    def _get_user_currency(self):
        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
        return currency_id or False

    name = fields.Char(related='partner_id.name', string='Branch Name', required=True, store=True, readonly=False)
    company_id = fields.Many2one('res.company', required=True)

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self._get_user_currency())
    # user_ids = fields.Many2many('res.users', 'res_company_users_rel', 'cid', 'user_id', string='Accepted Users')
    account_no = fields.Char(string='Account No.')
    street = fields.Char(compute='_compute_address', inverse='_inverse_street')
    street2 = fields.Char(compute='_compute_address', inverse='_inverse_street2')
    zip = fields.Char(compute='_compute_address', inverse='_inverse_zip')
    city = fields.Char(compute='_compute_address', inverse='_inverse_city')
    state_id = fields.Many2one('res.country.state', compute='_compute_address', inverse='_inverse_state',
                               string="Fed. State")
    country_id = fields.Many2one('res.country', compute='_compute_address', inverse='_inverse_country',
                                 string="Country")
    email = fields.Char(related='partner_id.email', store=True, readonly=False)
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False)
    website = fields.Char(related='partner_id.website', readonly=False)
    vat = fields.Char(related='partner_id.vat', string="Tax ID", readonly=False)
    company_registry = fields.Char()

    logo = fields.Binary(related='partner_id.image_1920', string="Branch Logo", readonly=False)
    external_report_layout_id = fields.Many2one('ir.ui.view', 'Document Template')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    report_header = fields.Text(string='Branch Tagline',
                                help="Appears by default on the top right corner of your printed documents (report header).")
    report_footer = fields.Text(string='Report Footer', translate=True,
                                help="Footer text displayed at the bottom of all reports.")

    def _get_company_address_fields(self, partner):
        return {
            'street': partner.street,
            'street2': partner.street2,
            'city': partner.city,
            'zip': partner.zip,
            'state_id': partner.state_id,
            'country_id': partner.country_id,
        }

    # TODO @api.depends(): currently now way to formulate the dependency on the
    # partner's contact address
    def _compute_address(self):
        for branch in self.filtered(lambda branch: branch.partner_id):
            address_data = branch.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = branch.partner_id.browse(address_data['contact']).sudo()
                branch.update(branch._get_company_address_fields(partner))

    def _inverse_street(self):
        for branch in self:
            branch.partner_id.street = branch.street

    def _inverse_street2(self):
        for branch in self:
            branch.partner_id.street2 = branch.street2

    def _inverse_zip(self):
        for branch in self:
            branch.partner_id.zip = branch.zip

    def _inverse_city(self):
        for branch in self:
            branch.partner_id.city = branch.city

    def _inverse_state(self):
        for branch in self:
            branch.partner_id.state_id = branch.state_id

    def _inverse_country(self):
        for branch in self:
            branch.partner_id.country_id = branch.country_id

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def on_change_country(self, country_id):
        # This function is called from account/models/chart_template.py, hence decorated with `multi`.
        self.ensure_one()
        currency_id = self._get_user_currency()
        if country_id:
            currency_id = self.env['res.country'].browse(country_id).currency_id
        return {'value': {'currency_id': currency_id.id}}

    @api.onchange('country_id')
    def _onchange_country_id_wrapper(self):
        res = {'domain': {'state_id': []}}
        if self.country_id:
            res['domain']['state_id'] = [('country_id', '=', self.country_id.id)]
        values = self.on_change_country(self.country_id.id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)
        return res

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('partner_id'):
            return super(ResBranch, self).create(vals)
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            'image_1920': vals.get('logo'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'website': vals.get('website'),
            'vat': vals.get('vat'),
        })
        # compute stored fields, for example address dependent fields
        partner.flush()
        vals['partner_id'] = partner.id
        branch = super(ResBranch, self).create(vals)
        # The write is made on the user to set it automatically in the multi company group.
        self.env.user.write({'branch_ids': [(4, branch.id)]})

        # Make sure that the selected currency is enabled
        if vals.get('currency_id'):
            currency = self.env['res.currency'].browse(vals['currency_id'])
            if not currency.active:
                currency.write({'active': True})
        return branch

    def write(self, values):
        # Make sure that the selected currency is enabled
        if values.get('currency_id'):
            currency = self.env['res.currency'].browse(values['currency_id'])
            if not currency.active:
                currency.write({'active': True})

        return super(ResBranch, self).write(values)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if self._context.get('branch_id'):
            recs = self.search([('id', 'in', self.env.user.branch_ids.ids)] + args, limit=limit)
            return recs.name_get()
        return super(ResBranch, self).name_search(name=name, args=args, operator=operator, limit=limit)
