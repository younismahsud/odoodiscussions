from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    test_amount = fields.Float('Test Amount')

    def open_sale_order_lines(self):
        domain = [('product_id', '=', self.product_id.id), ('order_id.partner_id', '=', self.order_id.partner_id.id)]
        return {
            'name': _('Sales history'),
            'res_model': 'sale.order.line',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {},
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('od_sale_custom.view_order_line_tree2').id, 'tree')]
        }

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({'test_amount': self.test_amount})
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cust_email = fields.Char('Email')
    duration = fields.Float('Duration')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        print(invoice_vals, "Before")
        invoice_vals['cust_email'] = self.cust_email
        print(invoice_vals, "after")
        return invoice_vals
