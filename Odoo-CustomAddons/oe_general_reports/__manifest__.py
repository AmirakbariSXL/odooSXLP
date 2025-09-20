# -*- coding: utf-8 -*-
{
    'name': "General Reports Customization",
    'summary': "Customize reports in Odoo according to specific requirements",
    'description': """
        This module allows customization of reports in Odoo to meet specific needs and requirements.
    """,
    'author': "Odooers",
    'website': "https://www.odooers.ir/",
    'category': 'Customizations',
    'version': '18.0.1.0',
    'depends': ['base','sale','account'],
    'data': [
        'views/res_company_views.xml',
        
        'report/report_paperformats.xml',
        'report/report_actions.xml',        
        'report/report_layout.xml',
        'report/sale_order_templates.xml',
        'report/account_move_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [         
            'oe_general_reports/static/src/styles/*.scss'
        ],
    },
}