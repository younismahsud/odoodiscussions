from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
