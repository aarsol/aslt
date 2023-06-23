import logging
from odoo import http
from odoo.http import request, serialize_exception as _serialize_exception, content_disposition
from odoo import api, fields, models, tools, _
import datetime
from werkzeug import urls
import functools
import urllib
import requests
import re
import pdb

_logger = logging.getLogger(__name__)
try:
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class SendSMS(models.Model):
    _name = "send_sms"
    _description = "Send SMS"

    name = fields.Char(required=True, string='Name')
    gateway_id = fields.Many2one('gateway_setup', required=True, string='SMS Gateway')
    model_id = fields.Many2one('ir.model', string='Applies to',
                               help="The kind of document with with this template can be used")
    sms_to = fields.Char(string='To (Mobile)', help="To mobile number (placeholders may be used here)")
    sms_html = fields.Text('Body')
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', 'Sidebar action', readonly=True, copy=False,
                                        help="Sidebar action to make this template available on records " "of the related document model")
    # ref_ir_value = fields.Many2one('ir.values', 'Sidebar Button', readonly=True, copy=False,
    #                                help="Sidebar button to open the sidebar action")

    @api.model
    def send_sms(self, template_id, record_id):
        sms_rendered_content = self.env['send_sms'].render_template(template_id.sms_html, template_id.model_id.model,
                                                                    record_id)
        rendered_sms_to = self.env['send_sms'].render_template(template_id.sms_to, template_id.model_id.model,
                                                               record_id)
        self.send_sms_link(sms_rendered_content, rendered_sms_to, record_id, template_id.model_id.model,
                           template_id.gateway_id)

    def send_sms_link(self, sms_rendered_content, rendered_sms_to, record_id, model, gateway_url_id):
        # sms_rendered_contents = sms_rendered_content.encode('ascii', 'ignore')
        sms_rendered_content_msg = urllib.parse.quote_plus(sms_rendered_content)
        if rendered_sms_to:
            rendered_sms_to = re.sub(r' ', '', rendered_sms_to)
            if '+' in rendered_sms_to:
                rendered_sms_to = rendered_sms_to.replace('+', '')
            if '-' in rendered_sms_to:
                rendered_sms_to = rendered_sms_to.replace('-', '')

        if rendered_sms_to:
            send_url = gateway_url_id.gateway_url
            send_link = send_url.replace('{mobile}', rendered_sms_to).replace('{message}', sms_rendered_content_msg)
            response = requests.request("GET", url=send_link).text
            self.env['sms_track'].sms_track_create(record_id, sms_rendered_content, rendered_sms_to, response, model,
                                                   gateway_url_id.id)
            if model not in ('gateway_setup', 'res.users'):
                self.env['mail.message'].create({
                    # 'author_id': http.request.env.user.partner_id.id,
                    'author_id': self.env.user.partner_id.id,
                    'date': datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    'model': model,
                    'res_id': record_id,
                    'message_type': 'email',
                    'body': '<b>SMS: </b>' + sms_rendered_content,
                })
            return response

    def render_template(self, template, model, res_id):
        template = mako_template_env.from_string(tools.ustr(template))
        user = self.env.user
        record = self.env[model].browse(res_id)
        variables = {'user': user}
        variables['object'] = record
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.error("Failed to render template %r using values %r" % (template, variables))
            render_result = u""
        if render_result == u"False":
            render_result = u""

        return render_result

    def create_action(self):
        action_obj = self.env['ir.actions.act_window'].sudo()
        view = self.env.ref('send_sms.sms_compose_wizard_form')
        src_obj = self.model_id.model
        button_name = _('SMS Send (%s)') % self.name
        action = action_obj.create({
            'name': button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'sms.compose',
            'src_model': src_obj,
            'view_type': 'form',
            'context': "{'default_template_id' : %d, 'default_use_template': True}" % (self.id),
            'view_mode': 'form,tree',
            'view_id': view.id,
            'target': 'new',
            'auto_refresh': 1,
            'binding_model_id': self.model_id.id,
        })
        self.write({
            'ref_ir_act_window': action.id,
        })
        return True

    def unlink_action(self):
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.sudo().unlink()
        return True


class SendSMSCron(models.Model):
    _name = "send_sms.cron"
    _description = "Send SMS Cron"

    template_id = fields.Many2one('send_sms')
    res_id = fields.Integer()
    status = fields.Boolean(default=False)

    def send_sms(self):
        messages = self.env['send_sms.cron'].search([('status', '=', False)], limit=10)
        for message in messages:
            self.env['send_sms'].send_sms(message.template_id, message.res_id)
            message.status = True
            self._cr.commit()
