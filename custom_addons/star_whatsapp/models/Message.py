from odoo import models, fields, api


class star_whatsapp(models.Model):
    _name = 'star_whatsapp.message'
    _description = 'Star Whatsapp: Mensaje'


    number = fields.Char(string='Número', required=True)
    message = fields.Text(string='Mensaje', required=True)

    