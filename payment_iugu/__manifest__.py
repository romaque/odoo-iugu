# -*- coding: utf-8 -*-
{
    'name': "Método de Pagamento Iugu",
    'summary': "Payment Acquirer: Iugu Implementation",
    'description': """Iugu payment gateway for Odoo.""",
    'author': "Romaque Máximo, Danimar Ribeiro",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['account', 'payment'],
    'external_dependencies': {
        'python': ['iugu'],
    },
    'data': [
        'views/payment_views.xml',
        'views/iugu.xml',
        'data/iugu.xml',
    ],
    'installable': True,
    'auto_install': True,
}
