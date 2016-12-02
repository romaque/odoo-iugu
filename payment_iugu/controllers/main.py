# -*- coding: utf-8 -*-
import logging
import pprint
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IuguController(http.Controller):
    _notify_url = '/iugu/notificacao/'
    _status_url = '/iugu/status/'

    @http.route(
        '/iugu/notificacao/', type='http', auth="none",
        methods=['GET', 'POST'], csrf=False)
    def iugu_form_feedback(self, **post):
        request.env['payment.transaction'].sudo().form_feedback(post, 'iugu')
        return "<status>OK</status>"

    @http.route('/iugu/status/', type='http', auth="none",
                methods=['GET', 'POST'], csrf=False)
    def cielo_status(self, **post):
        """ Quando o status de uma transação modifica essa url é chamada
        checkout_iugu_order_number 708da2506ec44d64aade742c11509459
        order_number SO00
        payment_status paid
            pending - Pendente (Para todos os meios de pagamento)
            paid - Pago (Para todos os meios de pagamento)
            canceled - Cancelado (Para todos os meios de pagamento)
        """
        _logger.info(
            u'Iniciando mudança de status de transação post-data: %s',
            pprint.pformat(post))  # debug
        self.iugu_validate_data(**post)
        return "<status>OK</status>"
