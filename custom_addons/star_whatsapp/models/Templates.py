from odoo import fields, models, api


class WhatsappTemplate(models.Model):
    _name = 'star_whatsapp.templates'
    _description = 'Star Whatsapp: Plantillas WhatsApp'

    name = fields.Char(string="Nombre Plantilla", required=True)
    body = fields.Text(string="Contenido", required=True)
    model_id = fields.Many2one(comodel_name='ir.model', string="Aplica a modelo")