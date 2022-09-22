from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal


class OdooAcademy(http.Controller):

    @http.route('/academy/courses/', auth='public', website=True)
    def display_subjects(self, sortby=None, **kw):
        searchbar_sortings = {
            'date': {'label': _('Course Date'), 'order': 'course_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        print(order)
        courses = http.request.env['openacademy.course'].search([('state', 'in', ('draft', 'in-progress', 'completed'))], order=order)
        return http.request.render('openacademy.portal_openacademy_courses', {
            'courses': courses,
            'page_name': 'course',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })

    @http.route('/academy/<model("openacademy.course"):course>/', auth='public', website=True)
    def display_course_detail(self, course):
        return http.request.render('openacademy.course_detail', {'course': course, 'page_name': 'course'})


class AcademyCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(AcademyCustomerPortal, self)._prepare_home_portal_values()
        count_courses = http.request.env['openacademy.course'].search_count([('state', 'in', ('draft', 'in-progress', 'completed'))])
        values.update({
            'count_courses': count_courses,
        })
        return values
