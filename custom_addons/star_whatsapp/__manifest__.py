{
    'name': "Envios de Whatsapp",

    'summary': "Módulo para envio de Whatsapp mediante Evolution API",

    'description': """
            Módulo de integración de WhatsApp para Odoo mediante Evolution API.

Este módulo permite enviar mensajes de WhatsApp directamente desde Odoo
utilizando instancias configuradas en Evolution API. Está diseñado para
automatizar la comunicación con clientes, proveedores o contactos desde
los diferentes procesos del sistema.

Características principales:

- Envío de mensajes de WhatsApp desde Odoo.
- Soporte para múltiples instancias (diferentes números de WhatsApp).
- Registro de mensajes enviados con número de destino.
- Posibilidad de adjuntar archivos o documentos.
- Integración sencilla para usar desde otros módulos o automatizaciones.
- Base preparada para integraciones con CRM, ventas, facturación o notificaciones.

El módulo está pensado como una capa de integración entre Odoo y Evolution API,
permitiendo extender fácilmente funcionalidades como:

- Envío automático mediante acciones programadas (cron).
- Notificaciones automáticas a clientes.
- Integraciones con procesos de negocio personalizados.

Requiere una instancia activa de Evolution API configurada previamente.
    """,

    'author': "Jonathan Moreno",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Notifications',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','crm'],
    'installable': True,
    'application': True,
    # always loaded
    'data': [
        'security/Groups.xml',
        'security/ir.model.access.csv',
        # views
        'views/MainMenu.xml',
        'views/Config.xml',
        'views/Instances.xml',
        'views/Messages.xml',
        'views/Crm/Lead.xml',
        'views/WhatsappWizard.xml',
        # Data
        'data/EvoConfig.xml',
        # Cron
        'views/Cron/SendWhatsappMessages.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
