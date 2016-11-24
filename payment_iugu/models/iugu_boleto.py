# -*- coding: utf-8 -*-

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.osv import osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _
from iugu import Invoice

import logging
import pprint
import os
import datetime

_logger = logging.getLogger(__name__)

os.environ["IUGU_API_TOKEN"] = "SEU_IUGU_API_TOKEN"

class IuguBoleto(osv.Model, Invoice):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('iugu', 'Iugu Boleto Bancário')])

    def iugu_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/iugu/feedback'

    @api.multi
    def iugu_form_generate_values(self, values):
        # TODO Aqui retorna os valores que são usados na
        # renderização do botão de pagamento
        return {
            'nome': 'nome',
            'item_name': 'aa',
        }
    
    def _create_iugu_invoice(self, data):

        nome = data.get('name')
        item_name = data.get('item_name')
        email = data.get('email')
        address = data.get('address')
        city = data.get('city')
        zip = data.get('zip')
        country = data.get('country')
        item_number = data.get('item_number')
        amount = int(data.get('amount', '0'))
        today = datetime.date.today()

        dados_invoice = {
            'email': email,
            'due_date': today.strftime('%d/%m/%Y'),
            'items': [{
                      'description': item_name,
                      'quantity': item_number,
                      'price_cents': amount * 100
                      }],
            'payer': {
                'name': nome,
                'address': {
                    'street': address,
                    'city': city,
                    'country': country,
                    'zip_cod': zip
                }
            }
        }

        invoice = Invoice()
        result = invoice.create(dados_invoice)

        _logger.info(pprint.pformat(result))
