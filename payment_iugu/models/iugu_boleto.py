# -*- coding: utf-8 -*-

import os
import logging
import pprint
import datetime

from iugu import Invoice
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class IuguBoleto(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('iugu', 'Iugu Boleto Bancário')])

    iugu_api_key = fields.Char('Iugu Api Token', required_if_provider='iugu', groups='base.group_user')

    def iugu_get_form_action_url(self):
        return '/payment/iugu/feedback'

    # Esses parametros aqui serão enviados via post, é muito importante
    # retornar a url para onde esses dados serão enviados. e.g tx_url
    @api.multi
    def iugu_form_generate_values(self, values):

        iugu_tx_values = dict(values)
        iugu_tx_values.update({
            'cmd': '_xclick',
            'item_name': '%s: %s' % (self.company_id.name, values['reference']),
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


class TransactionIugu(models.Model):
    _inherit = 'payment.transaction'

    # Aqui pode colocar campos especificos da transaçaõ do iugu
    iugu_id = fields.Char(string=u'ID Transação')

    @api.model
    def _iugu_form_get_tx_from_data(self, data):

        # Este método é chamada com os dados recebidos do iugu para
        # pesquisar e retornar a transação já cadastrada no odoo
        reference = data.get('reference')
        tx = self.search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = 'received data for reference %s' % pprint.pformat(reference)
            if not tx:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)

        return tx

    @api.multi
    def _iugu_form_validate(self, data):

        _logger.info(pprint.pformat(data))

        if self.state == 'done':
            return True

        invoice = self.env['payment.token'].sudo().create({
            'name': data['name'],
            'item_name': data['item_name'],
            'email': data['email'],
            'address': data['address1'],
            'city': data['city'],
            'zip': data['zip'],
            'acquirer_id': self.acquirer_id.id,
            'partner_id': self.partner_id.id,
            'item_number': data['item_number'],
            'country': data['country'],
            'amount': data['amount']
        })

        values = {
            'acquirer_reference': invoice['acquirer_ref'],
            'state': 'pending',
        }

        return self.write(values)

class PaymentTokenIugu(models.Model):
    _inherit = 'payment.token'

    @api.model
    def iugu_create(self, values):

        today = datetime.date.today()

        acquirer = self.env['payment.acquirer'].browse(values['acquirer_id'])

        os.environ["IUGU_API_TOKEN"] = acquirer.iugu_api_key

        dados_invoice = {
            'email': values['email'],
            'due_date': today.strftime('%d/%m/%Y'),
            'items': [{
                      'description': values['item_name'],
                      'quantity': 1,
                      'price_cents': int(float(values['amount'])) * 100
                      }],
            'payer': {
                'name': values['name'],
                'address': {
                    'street': values['address'],
                    'city': values['city'],
                    'country': values['country'],
                    'zip_cod': values['zip']
                }
            }
        }

        invoice = Invoice()
        result = invoice.create(dados_invoice)

        return {
            'acquirer_ref': result['id']
        }