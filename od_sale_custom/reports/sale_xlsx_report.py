from odoo import models, fields, api, _
import base64
import io


class SaleXlsxReport(models.AbstractModel):
    _name = 'report.od_sale_custom.report_saleorder_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def add_company_header(self, row, sheet, company, bold):
        company_name = company.name
        address = f"{company.street} {company.street2}"
        country = company.country_id.name
        if company.logo:
            image_data = io.BytesIO(base64.b64decode(company.logo))
            sheet.insert_image(row, 1, 'logo.png', {'image_data': image_data, 'x_scale': 0.10, 'y_scale': 0.10})
            sheet.write(row+2, 1, company_name, bold)
            sheet.write(row+3, 1, address)
            sheet.write(row+4, 1, country)

    def add_partner_address(self, row, col, sheet, partner, bold, shipping=True):
        partner_name = partner.display_name
        address = f"{partner.street} {partner.street2}"
        country = partner.country_id.name
        phone = partner.phone
        if shipping:
            sheet.write(row, col, "Invoicing and Shipping Address:", bold)
        sheet.write(row+1, col, partner_name)
        sheet.write(row+2, col, address)
        sheet.write(row+3, col, country)
        sheet.write(row+4, col, phone)

    def generate_xlsx_report(self, workbook, data, orders):
        row = 1
        for order in orders:
            sheet = workbook.add_worksheet(order.name)
            bold = workbook.add_format({"bold": True})
            heading = workbook.add_format({"font_size": 18})
            date_style = workbook.add_format({'num_format': 'yyyy-mm-dd'})
            center_style = workbook.add_format({'valign': 'center', 'bold': True})
            wrap_text = workbook.add_format({'text_wrap': True})
            money = workbook.add_format({'num_format': '$#,##0.00'})
            white_bg = workbook.add_format({'bg_color': 'white'})
            bottom_border = workbook.add_format({'bottom': True})
            left_border = workbook.add_format({'left': True})
            company = self.env.company
            partner = order.partner_id
            shipping_partner = order.partner_shipping_id
            self.add_company_header(row, sheet, company, bold)
            row += 6
            self.add_partner_address(row, 1, sheet, shipping_partner, bold)
            self.add_partner_address(row, 6, sheet, partner, bold, shipping=False)
            row += 6
            sheet.write(row, 1, f"Quotation # {order.name}", heading)
            row += 1
            sheet.write(row, 1, "Quotation Date:")
            sheet.write(row, 3, "Salesperson:")
            row += 1
            sheet.write(row, 1, order.date_order, date_style)
            sheet.write(row, 3, order.user_id.name)
            row += 2
            sheet.merge_range(row, 1, row, 2, 'Description', bold)
            sheet.write(row, 3, 'Quantity', center_style)
            sheet.merge_range(row, 4, row, 5, 'Quantity Delivered', center_style)
            sheet.merge_range(row, 6, row, 7, 'Quantity Invoiced', center_style)
            sheet.merge_range(row, 8, row, 9, 'Unit Price', center_style)
            sheet.write(row, 10, 'Amount', center_style)
            row += 1
            for line in order.order_line:
                sheet.merge_range(row, 1, row, 2, line.name, wrap_text)
                sheet.write(row, 3, line.product_uom_qty, center_style)
                sheet.merge_range(row, 4, row, 5, line.qty_delivered, center_style)
                sheet.merge_range(row, 6, row, 7, line.qty_invoiced, center_style)
                sheet.merge_range(row, 8, row, 9, line.price_unit, money)
                sheet.write(row, 10, line.price_subtotal, money)
                row += 1

            sheet.conditional_format(f"A1:M{row+4}", {'type': 'formula', 'criteria': 'True', 'format': white_bg})
            sheet.conditional_format(f"A{row+4}:M{row+4}", {'type': 'formula', 'criteria': 'True', 'format': bottom_border})
            sheet.conditional_format(f"N1:N{row+4}", {'type': 'formula', 'criteria': 'True', 'format': left_border})
