from odoo import http


class OdooAcademy(http.Controller):

    @http.route('/academy/subjects/', auth='public')
    def index(self, **kw):
        return "Hello World! Here are the available subjects"