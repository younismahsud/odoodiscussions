{
    'name': 'Product Sales history',
    'description': """
       ** Button on sale order line to show product sale history.
    """,
    'author': 'Younis',
    'depends': ['sale', 'report_xlsx'],
    'data': [
        'views/sale.xml',
        'reports/report.xml',
        'views/invoice.xml',
    ],
    'installable': True,
}