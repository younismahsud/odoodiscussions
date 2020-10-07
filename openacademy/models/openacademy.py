from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'Courses'

    name = fields.Char(string='Course Name', required=True)
    description = fields.Text('Description', help='Add course description here...')
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")


class Session(models.Model):
    _name = 'openacademy.session'
    _description = "OpenAcademy Sessions"

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.date.today())
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    instructor_id = fields.Many2one('res.partner', string="Instructor", domain=[('country_id', '=', 'Belgium')])
    country_id = fields.Many2one('res.country', related='instructor_id.country_id')
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    active = fields.Boolean(string='Active', default=True)

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

