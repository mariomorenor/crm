from odoo import fields, models, api
from odoo.exceptions import UserError

from io import BytesIO
import requests
import qrcode
import base64


class EvoConfig(models.Model):
    _name = 'star_whatsapp.config'
    _description = 'Star Whatsapp: Config'

    host = fields.Char(string='Servidor Evolution API', required=True)
    api_key = fields.Char(string='API Key', required=True)

    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            raise UserError("Configura Evolution API primero")
        return config

class Instance(models.Model):
    _name = 'star_whatsapp.instances'
    _description = 'Star Whatsapp: Instancia'
    _sql_constraints = [
        ('unique_instance_name', 'unique(name)', 'El nombre de la instancia ya existe.')
    ]

    name = fields.Char(string="Nombre de Instancia", required=True)
    number = fields.Char(string='Número', required=True)
    qr_code = fields.Image(string="QR")
    state = fields.Selection(string="Estado", selection=[
        ('created', 'Creado'),
        ('connecting', 'Esperando conexión'),
        ('connected', 'Conectado')
    ])

    def create_instance(self):
        config = self.env['star_whatsapp.config'].search([], limit=1)
        if not config:
            raise UserError("No hay configuración de Evolution API")

        url = f"{config.host}/instance/create"

        payload = {
            "instanceName": self.name,
            "integration": "WHATSAPP-BAILEYS",
            "number": self.number,
            "qrcode": True
        }

        headers = {
            "apikey": config.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 201 and response.status_code != 200:
            raise UserError(f"Error creando instancia: {response.text}")

        data = response.json()
        self.state = data.get("instance", {}).get("status")

        qr_data = data.get("qrcode", {})
        qr_string = qr_data.get("code")

        if qr_string:
            self._generate_qr(qr_string)

    def update_qr(self):

        config = self.env['star_whatsapp.config'].sudo().search([], limit=1)

        if not config:
            raise UserError("No hay configuración de Evolution API")

        url = f"{config.host}/instance/connect/{self.name}"

        headers = {
            "apikey": config.api_key
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise UserError(response.text)

        data = response.json()
        status = data.get("instance", {}).get("state") or data.get("state")

        if status:
            # Mapear estados si es necesario
            if status.lower() in ['open', 'connected']:
                self.state = 'connected'
                self.qr_code = False  # limpiar QR
                return
            else:
                self.state = 'connecting'

        qr_string = (data.get("qrcode") or {}).get("code") or data.get("code")

        if qr_string:
            self._generate_qr(qr_string)

    def _generate_qr(self, qr_string):

        qr = qrcode.make(qr_string)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        self.qr_code = base64.b64encode(buffer.getvalue())

    @api.model
    def create(self, values):
        res = super(Instance, self).create(values)
        try:
            res.create_instance()
        except UserError as e:
            raise e
        return res

    def unlink(self):

        config = self.env['star_whatsapp.config'].sudo().search([], limit=1)
        if not config:
            raise UserError("No hay configuración de Evolution API")

        headers = {
            "apikey": config.api_key
        }

        for record in self:
            url = f"{config.host}/instance/delete/{record.name}"

            try:
                response = requests.delete(url, headers=headers)

                if response.status_code not in [200, 201, 204]:
                    raise UserError(
                        f"Error Eliminando instancia {record.name}: {response.text}"
                    )

            except Exception as e:
                raise UserError(f"Error de conexión: {str(e)}")

        return super(Instance, self).unlink()