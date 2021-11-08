from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.tools.misc import get_lang
import logging
from odoo.tools.profiler import profile

logger = logging.getLogger("*___OpenAcademy___*")


class Course(models.Model):
    _name = 'openacademy.course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Courses'
    _rec_name = 'course_name'

    name = fields.Char(string="Course Number", required=True, index=True, copy=False, readonly=True, default=_('New'))
    course_name = fields.Char(string='Course Name', required=True, translate=True, tracking=True)
    description = fields.Text('Description', help='Add course description here...')
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True, tracking=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancel', 'Cancel')
                              ], string='Status', readonly=False, tracking=True, default='draft', copy=False)
    course_date = fields.Date('Course date', required=True, default=fields.Date.today())

    def action_submit(self):
        self.state = 'submitted'
        users = self.env.ref('openacademy.group_course_approval').users
        for user in users:
            self.activity_schedule('openacademy.mail_act_course_approval', user_id=user.id, note=f'Please Approve course {self.name}')

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.name}] {record.course_name}"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            course_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
            if not course_ids:
                course_ids = self._search([('course_name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        else:
            course_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(course_ids).with_user(name_get_uid))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            course_date = vals.get('course_date')
            vals['name'] = self.env['ir.sequence'].next_by_code('openacademy.course', sequence_date=course_date)
        return super(Course, self).create(vals)

    def action_validate(self):
        for record in self:
            logger.info(f"Course {record.course_name} state moved to In progress by {self.env.user.name}")
            record.write({'state': 'in_progress'})
            activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id),
                                                            ('activity_type_id', '=', self.env.ref('openacademy.mail_act_course_approval').id)])
            activity_id.action_feedback(feedback='Approved')
            other_activity_ids = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('activity_type_id', '=', self.env.ref('openacademy.mail_act_course_approval').id)])
            other_activity_ids.unlink()

    def action_completed(self):
        for record in self:
            record.write({'state': 'completed'})

    def action_cancel(self):
        for record in self:
            logger.error(f"Course {record.course_name} state moved to Cancelled by {self.env.user.name}")
            record.write({'state': 'cancel'})

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [(_('course_name', '=like', u"Copy of {}%").format(self.course_name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.course_name)
        else:
            new_name = u"Copy of {} ({})".format(self.course_name, copied_count)

        default['course_name'] = new_name
        return super(Course, self).copy(default)

    _sql_constraints = [
        ('name_description_check',
         'check (course_name != description)',
         'The course name and description can not be same.'),

        ('course_name_unique',
         'unique(course_name)',
         'Course name should be unique'),
    ]


class Session(models.Model):
    _name = 'openacademy.session'
    _description = "OpenAcademy Sessions"

    def get_default_duration(self):
        ICP = self.env['ir.config_parameter'].sudo()
        default_duration = ICP.get_param('openacademy.session_duration')
        return default_duration

    def get_default_seats(self):
        ICP = self.env['ir.config_parameter'].sudo()
        default_seats = ICP.get_param('openacademy.session_allowed_seats')
        return default_seats

    @api.onchange('course_id', 'instructor_id')
    def _get_instructor_domain(self):
        return {'domain': {'instructor_id': [('id', '=', self.course_id.responsible_id.partner_id.id)]}}

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.date.today())
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=get_default_duration)
    end_date = fields.Date(string="End Date", store=True, compute='_get_end_date', inverse='_set_end_date')
    seats = fields.Integer(string="Number of seats", default=get_default_seats)
    instructor_id = fields.Many2one('res.partner', string="Instructor")
    country_id = fields.Many2one('res.country', related='instructor_id.country_id')
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    active = fields.Boolean(string='Active', default=True)
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)
    color = fields.Integer()
    email_sent = fields.Boolean('Email Sent', default=False)
    image_1920 = fields.Image("Image")

    def number_of_attendees(self):
        return len(self.attendee_ids)

    def action_send_session_by_email_cron(self):
        session_ids = self.env['openacademy.session'].search([('email_sent', '=', False)])
        for session in session_ids:
            if session.email_sent is False:
                session.action_send_session_by_email()
                session.email_sent = True

    @profile()
    def action_send_session_by_email(self):
        # for attendee in self.attendee_ids:
        ctx = {}
        email_list = self.attendee_ids.mapped('email')
        if email_list:
            ctx['email_to'] = ','.join([email for email in email_list if email])
            ctx['email_from'] = self.env.user.company_id.email
            ctx['send_email'] = True
            ctx['attendee'] = ''
            template = self.env.ref('openacademy.email_template_openacademy_session')
            template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise ValidationError("A session's instructor can't be an attendee")

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }

