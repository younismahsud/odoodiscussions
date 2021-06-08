from odoo import models, fields, api
from odoo import tools


class ProductSaleAnalysis(models.Model):
    _name = 'product.sale.analysis'
    _auto = False
    _description = 'Product Sale Analysis'

    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Date('Invoice Date')
    quantity = fields.Float('Quantity')
    untaxed_total = fields.Float('Untaxed')
    total = fields.Float('Total')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
    ], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='Invoice Status', readonly=True)
    exclude_from_invoice_tab = fields.Boolean('Exclude from invoice')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'product_sale_analysis')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW product_sale_analysis AS (
                SELECT
                    row_number() OVER () AS id,
                    line.product_id,
                    line.date,
                    line.quantity,
                    line.untaxed_total,
                    line.total,
                    line.invoice_id,
                    line.partner_id,
                    line.user_id,
                    line.type,
                    line.state,
                    line.exclude_from_invoice_tab FROM (
                        SELECT
                            p.id as product_id,
                            am.invoice_date as date,
                            (aml.quantity * invoice_type.sign_qty) as quantity,
                            (aml.price_subtotal * invoice_type.sign_qty) as untaxed_total,
                            (aml.price_total * invoice_type.sign_qty) as total,
                            aml.move_id as invoice_id,
                            am.partner_id as partner_id,
                            am.invoice_user_id as user_id,
                            am.type as type,
                            am.state as state,
                            aml.exclude_from_invoice_tab as exclude_from_invoice_tab
                        FROM product_product p
                        LEFT JOIN account_move_line aml ON (p.id = aml.product_id)
                        LEFT JOIN account_move am ON (aml.move_id = am.id)
                        JOIN (
                            SELECT id,(CASE
                                 WHEN am.type::text = ANY (ARRAY['in_refund'::character varying::text, 'in_invoice'::character varying::text])
                                    THEN -1
                                    ELSE 1
                                END) AS sign,(CASE
                                 WHEN am.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                                    THEN -1
                                    ELSE 1
                                END) AS sign_qty
                            FROM account_move am
                        ) AS invoice_type ON invoice_type.id = am.id
                    ) as line
                    WHERE
                        line.state = 'posted' AND
                        not line.exclude_from_invoice_tab AND
                        line.type in ('out_invoice', 'out_refund')
                )""")
