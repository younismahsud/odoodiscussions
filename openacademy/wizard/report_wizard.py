from odoo import models, fields, api


class OpenAcademyPDFReport(models.TransientModel):
    _name = 'openacademy.pdf.report'

    date_from = fields.Date('Date from', required=True)
    date_to = fields.Date('Date to', required=True)
    course_ids = fields.Many2many('openacademy.course', string='Course')
    responsible_id = fields.Many2one('res.users', 'Responsible')

    def action_print_report(self):
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'course_ids': self.course_ids.ids, 'responsible_id': self.responsible_id.id}
        return self.env.ref('openacademy.action_openacademy_pdf_report').report_action(self, data=data)


class OpenAcademyReportPDF(models.AbstractModel):
    _name = 'report.openacademy.openacademy_pdf_template'

    def _get_report_values(self, docids, data=None):
        domain = [('state', '!=', 'cancel')]
        if data.get('date_from'):
            domain.append(('course_date', '>=', data.get('date_from')))
        if data.get('date_to'):
            domain.append(('course_date', '<=', data.get('date_to')))
        if data.get('course_ids'):
            domain.append(('id', 'in', data.get('course_ids')))
        if data.get('responsible_id'):
            domain.append(('responsible_id', '=', data.get('responsible_id')))
        docs = self.env['openacademy.course'].search(domain)
        responsible = self.env['res.users'].browse(data.get('responsible_id'))
        course_ids = self.env['openacademy.course'].browse(data.get('course_ids'))
        data.update({'responsbile': responsible.name})
        data.update({'courses': ",".join([course.course_name for course in course_ids])})
        return {
            'doc_ids': docs.ids,
            'doc_model': 'openacademy.course',
            'docs': docs,
            'datas': data
        }