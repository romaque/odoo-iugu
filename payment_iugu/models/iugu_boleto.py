# -*- coding: utf-8 -*-

import os
import logging
import pprint
import datetime

from odoo import api, fields, models
from odoo.http import request

_logger = logging.getLogger(__name__)
odoo_request = request

try:
    from iugu import Invoice
except ImportError:
    _logger.debug('Não é possível importar iugu')


class IuguBoleto(models.Model):
    _inherit = 'payment.acquirer'

    def _default_return_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return "%s%s" % (base_url, '/shop/confirmation')

    provider = fields.Selection(
        selection_add=[('iugu', 'Iugu Boleto Bancário')])
    iugu_api_key = fields.Char('Iugu Api Token')
    return_url = fields.Char(string="Url de Retorno",
                             default=_default_return_url,
                             size=300)

    @api.multi
    def iugu_form_generate_values(self, values):
        """ Função para gerar HTML POST do Iugu """
        order = odoo_request.website.sale_get_order()

        if not order or not order.payment_tx_id:
            return {
                'checkout_url': '/shop/payment',
            }

        items = []
        total_desconto = 0
        for line in order.order_line:
            total_desconto += line.discount

            item = {
                'description': line.product_id.name,
                'quantity': int(line.product_uom_qty),
                'price_cents': int(line.price_unit) * 100
            }

            items.append(item)

        today = datetime.date.today()

        dados_invoice = {
            'email': values.get('partner_email'),
            'due_date': today.strftime('%d/%m/%Y'),
            'items': items,
            'payer': {
                'name': values.get('partner_name'),
                'address': {
                    'street': values.get('partner_address'),
                    'city': values.get('partner_city')
                }
            }
        }

        os.environ["IUGU_API_TOKEN"] = self.iugu_api_key

        invoice = Invoice()
        result = invoice.create(dados_invoice)

        _logger.info(pprint.pformat(result))

        return {
            'checkout_url': '/shop/confirmation'
        }


class TransactionIugu(models.Model):
    _inherit = 'payment.transaction'

    iugu_transaction_id = fields.Char(string=u'ID Transação')

    @api.model
    def _iugu_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        tx = self.search([('reference', '=', reference)])

        return tx

    @api.multi
    def _iugu_form_validate(self, data):
        reference = data.get('order_number')
        txn_id = data.get('checkout_iugu_order_number')
        iugu_id = data.get('tid', False)
        payment_type = data.get('payment_method_type')
        state = data.get('payment_status')

        state = 'done' if state == 'paid' else state

        values = {
            'reference': reference,
            'acquirer_reference': txn_id,
            'state': state,
            'date_validate': datetime.datetime.now(),
            'transaction_type': payment_type,
            'iugu_transaction_id': iugu_id
        }
        res = {}
        res.update({k: v for k, v in values.items() if v})
        return self.write(res)
