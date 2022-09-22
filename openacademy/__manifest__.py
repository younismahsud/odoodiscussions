{
    'name': "Open Academy",

    'summary': """Manage trainings""",

    'description': """
        Open Academy module for managing trainings:
            - training courses
            - training sessions
            - attendees registration
    """,

    'author': "Odoo Discussions",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'sale', 'report_xlsx', 'website', 'portal'],

    # always loaded
    'data': [
        'data/activity.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/openacademy.xml',
        'views/res_partner.xml',
        'reports/custom_header_footer.xml',
        'reports/paperformat.xml',
        'reports/reports.xml',
        'data/email_template.xml',
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'reports/sale_qweb_template.xml',
        'views/res_config_settings.xml',
        'wizard/report_wizard_view.xml',
        'reports/openacademy_pdf_report.xml',
        'reports/openacademy_xlsx_report.xml',
        'views/product_sale_analysis.xml',
        'views/template.xml',
        'views/templates.xml',
        'views/website_menus.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/icon.png'],
}
