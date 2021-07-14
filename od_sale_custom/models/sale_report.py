from odoo import models, fields, api


class SaleReport(models.Model):
    _inherit = "sale.report"

    payment_term_id = fields.Many2one('account.payment.term', 'Payment terms', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['payment_term_id'] = ", s.payment_term_id as payment_term_id"
        groupby += ', s.payment_term_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)