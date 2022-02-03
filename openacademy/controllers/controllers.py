from odoo import http


class OdooAcademy(http.Controller):

    @http.route('/academy/subjects/', auth='public')
    def display_subjects(self, **kw):
        # return "Hello World! Here are the available subjects"
        return http.request.render('openacademy.subjects', {
            'subjects':
                ['Math', 'English', 'Programming', 'Operating System'],
        })
