# from odoo import http


# class StarWhatsapp(http.Controller):
#     @http.route('/star_whatsapp/star_whatsapp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/star_whatsapp/star_whatsapp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('star_whatsapp.listing', {
#             'root': '/star_whatsapp/star_whatsapp',
#             'objects': http.request.env['star_whatsapp.star_whatsapp'].search([]),
#         })

#     @http.route('/star_whatsapp/star_whatsapp/objects/<model("star_whatsapp.star_whatsapp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('star_whatsapp.object', {
#             'object': obj
#         })

