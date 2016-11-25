# -*- coding: utf-8 -*-

import os
import logging
import pprint
import datetime

from iugu import Invoice
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

os.environ["IUGU_API_TOKEN"] = "SEU_IUGU_API_TOKEN"


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


class TransactionIugu(models.Model):
    _inherit = 'payment.transaction'

    # Aqui pode colocar campos especificos da transaçaõ do iugu
    iugu_id = fields.Char(string=u'ID Transação')

    @api.model
    def _iugu_form_get_tx_from_data(self, data):

        # Este método é chamada com os dados recebidos do iugu para
        # pesquisar e retornar a transação já cadastrada no odoo
        reference = data.get('reference')  # trocar aqui pela chave correta
        txs = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        return txs[0]

    @api.multi
    def _iugu_form_validate(self, data):
        # Esse metodo é chamado com os dados, aqui sim vai ser setado
        # um dos estados na transação, pending, done, error, authorized, cancel
        reference = data.get('order_number')
        iugu_id = data.get('tid', False)
        state_iugu = data.get('payment_status')

        values = {
            'reference': reference,
            'acquirer_reference': iugu_id,
            'state': state_iugu,
        }
        return self.write(values)
