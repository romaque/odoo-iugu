# -*- coding: utf-8 -*-

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.osv import osv
from openerp.tools.float_utils import float_compare
from iugu import Invoice
from odoo import api, fields, models, _

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

		iugu_tx_values = dict(values)
		iugu_tx_values.update({
	        'cmd': '_xclick',
	        'item_name': values['reference'],
	        'item_number': values['reference'],
	        'amount': values['amount'],
	        'currency_code': values['currency'] and values['currency'].name or '',
	        'address1': values.get('partner_address'),
	        'city': values.get('partner_city'),
	        'country': values.get('partner_country') and values.get('partner_country').code or '',
	        'state': values.get('partner_state') and (values.get('partner_state').code or values.get('partner_state').name) or '',
	        'email': values.get('partner_email'),
	        'zip_code': values.get('partner_zip'),
	        'name': values.get('partner_name'),
	        'last_name': values.get('partner_last_name'),
	    })
		return iugu_tx_values

    
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
