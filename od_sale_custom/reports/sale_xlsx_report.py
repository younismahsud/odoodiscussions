from odoo import models, fields, api, _


class SaleXlsxReport(models.AbstractModel):
    _name = 'report.od_sale_custom.report_saleorder_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, orders):
        for order in orders:
            sheet = workbook.add_worksheet("Report")
            bold = workbook.add_format({"bold": True})
            sheet.write(0, 0, order.name, bold)
