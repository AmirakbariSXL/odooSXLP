{
    'name': 'Pharmacy Management',
    'version': '18.0.0.0',
    'summary': 'Pharmacy management: medicines, batches, prescriptions, patients and doctors',
    'description': 'Alan Technologies LLP - Improved pharmacy management module for Odoo 18 with expiry alerts, prescriptions and basic dispensing.',
    'category': 'Healthcare',
    'author': 'Alan Technologies LLP',
    'website': 'https://alantechnologies.in/',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_template.xml',
        'data/cron.xml',
        'views/medicine_views.xml',
        'views/batch_views.xml',
        'views/prescription_views.xml',
        'views/doctor_views.xml',
        'views/patient_views.xml',
        'report/report_prescription.xml',
        'report/prescription_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # add css/js if required
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
}
