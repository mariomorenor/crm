from odoo import models
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = 'crm.lead'

    def action_open_whatsapp_wizard(self):
        self.ensure_one()

        phone = (
                self.phone
                or self.partner_id.mobile
                or self.partner_id.phone
        )

        if not phone:
            raise UserError("Este lead no tiene número de teléfono")

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'star_whatsapp.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_number': phone,
                'default_message': self.name or '',
                'default_partner_id': self.partner_id.id
            }
        }
