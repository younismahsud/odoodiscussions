from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    cust_email = fields.Char('Email')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    test_amount = fields.Float('Test Amount')
