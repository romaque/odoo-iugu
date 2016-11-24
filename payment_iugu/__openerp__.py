# -*- coding: utf-8 -*-
{
    'name': "Método de Pagamento Iugu",
    'summary': "Payment Acquirer: Iugu Implementation",
    'description': """Iugu payment gateway for Odoo.""",
    'author': "Romaque Máximo",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['account', 'payment'],
    'data': [
        'views/iugu.xml',
        'data/iugu.xml',
    ],
    'installable': True,
    'auto_install': True,
}
