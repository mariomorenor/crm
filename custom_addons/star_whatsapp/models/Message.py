from odoo import models, fields, api
from odoo.exceptions import UserError

import requests
import random
import mimetypes


class Message(models.Model):
    _name = 'star_whatsapp.messages'
    _description = 'Star Whatsapp: Mensaje'

    name = fields.Char(related='partner_id.name')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')
    number = fields.Char(string='Número', required=True)
    number_formatted = fields.Char(string='Número Con Formato', compute='_compute_number_formatted', store=True)
    message = fields.Text(string='Mensaje', required=True)
    file = fields.Binary(string="Adjunto")
    file_name = fields.Char(string="Nombre del archivo")
    delay = fields.Integer(string='Delay', required=False, default=lambda self: random.randint(2, 5))
    country_id = fields.Many2one(comodel_name='res.country', string="País",
                                 default=lambda self: self.env.company.country_id)

    state = fields.Selection(string="Estado", selection=[
        ('draft', 'Borrador'),
        ('queue', 'En Cola'),
        ('sent', 'Enviado'),
        ('error', 'Error')
    ], default='draft')

    instance_id = fields.Many2one(comodel_name='star_whatsapp.instances', string='Instancia', required=True)

    response = fields.Text(string="Observaciones")

    def send_messages(self):
        config = self.env['star_whatsapp.config'].get_config()

        records = self.search([('state', '=', 'queue')])

        for record in records:

            if not record.number_formatted:
                record.state = 'error'
                continue

            try:
                if record.file:
                    url = f"{config.host}/message/sendMedia/{record.instance_id.name}"
                    headers = {
                        "apikey": config.api_key,
                        "Content-Type": "application/json",
                    }
                    media_base64 = record.file.decode('utf-8')
                    mediatype, mimetype = record._get_media_info(record.file_name)

                    data = {
                        'number': record.number_formatted,
                        'delay': record.delay * 1000,
                        'caption': record.message or '',
                        'mediatype': mediatype,
                        'mimetype': mimetype,
                        'fileName': record.file_name,
                        "media": media_base64,

                    }

                    response = requests.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=7
                    )

                else:

                    url = f"{config.host}/message/sendText/{record.instance_id.name}"
                    headers = {
                        "Content-Type": "application/json",
                        "apikey": config.api_key
                    }
                    payload = {
                        "number": record.number_formatted,
                        "text": record.message,
                        "delay": record.delay * 1000,
                    }

                    response = requests.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=7
                    )

                record.response = response.text

                if response.status_code in (200, 201):
                    record.state = 'sent'
                else:
                    record.state = 'error'

            except Exception as e:
                record.state = 'error'
                record.response = str(e)
                print(e)

    def _format_number(self, number, country_code='593'):
        if not number:
            return False

        # limpiar caracteres
        number = number.strip().replace(" ", "").replace("-", "")

        # quitar +
        if number.startswith("+"):
            number = number[1:]

        # ⚠️ SI YA TIENE CÓDIGO INTERNACIONAL (genérico)
        if number.startswith(tuple(str(c) for c in range(1, 10))) and len(number) > 10:
            return f"+{number}"

        # quitar 0 inicial
        if number.startswith("0"):
            number = number[1:]

        return f"+{country_code}{number}"

    def _get_media_info(self, file_name):
        """Devuelve (mediatype, mimetype)"""
        if not file_name:
            return 'document', 'application/octet-stream'

        mimetype, _ = mimetypes.guess_type(file_name)

        if not mimetype:
            return 'document', 'application/octet-stream'

        if mimetype.startswith('image'):
            return 'image', mimetype
        elif mimetype.startswith('video'):
            return 'video', mimetype
        else:
            return 'document', mimetype

    @api.depends('number', 'country_id')
    def _compute_number_formatted(self):
        for rec in self:
            code = rec.country_id.phone_code or '593'
            rec.number_formatted = rec._format_number(rec.number, country_code=code)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.number = self.partner_id.phone
            self.country_id = self.partner_id.country_id or self.env.company.country_id

    def action_set_draft(self):
        for rec in self:
            rec.write({
                'state': 'draft',
                'response': False
            })

    def action_set_queue(self):
        for rec in self:
            rec.write({
                'state': 'queue',
                'response': False
            })


class WhatsappSendWizard(models.TransientModel):
    _name = 'star_whatsapp.send.wizard'

    number = fields.Char(string="Número", required=True)
    partner_id = fields.Many2one(string="Contacto", comodel_name='res.partner', required=True)
    message = fields.Text(string="Mensaje")
    template_id = fields.Many2one(comodel_name='star_whatsapp.templates', string="Plantilla")
    attachment_ids = fields.Many2many('ir.attachment')

    def action_apply_template(self):
        if self.template_id:
            self.message = self.template_id.body

    def action_send(self):
        instance = self.env['star_whatsapp.instances'].sudo().search([], limit=1, order='priority asc')
        for wiz in self:
            for attachment in wiz.attachment_ids:
                self.env['star_whatsapp.messages'].create({
                    'number': wiz.number,
                    'partner_id': wiz.partner_id.id,
                    'message': wiz.message,
                    'file': attachment.datas,
                    'file_name': attachment.name,
                    'instance_id': instance.id,
                    'state': 'queue',
                })

            # Si no hay adjuntos, igual enviar
            if not wiz.attachment_ids:
                self.env['star_whatsapp.messages'].create({
                    'number': wiz.number,
                    'partner_id': wiz.partner_id.id,
                    'message': wiz.message,
                    'instance_id': instance.id,
                    'state': 'queue'
                })
