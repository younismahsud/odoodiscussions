from odoo import http


class OdooAcademy(http.Controller):

    @http.route('/academy/courses/', auth='public', website=True)
    def display_subjects(self, **kw):
        # return "Hello World! Here are the available subjects"
        # return http.request.render('openacademy.subjects', {
        #     'subjects':
        #         ['Math', 'English', 'Programming', 'Operating System'],
        # })
        courses = http.request.env['openacademy.course'].search([('state', 'in', ('submitted', 'in-progress', 'completed'))])
        return http.request.render('openacademy.courses', {
            'courses': courses,
        })

