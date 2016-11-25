# -*- coding: utf-8 -*-
import logging
import werkzeug
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IuguController(http.Controller):
    _accept_url = '/payment/iugu/feedback'

    @http.route([
        '/payment/iugu/feedback',
    ], type='http', auth='none', csrf=False)
    def iugu_form_feedback(self, **post):

        res = request.env['payment.transaction'].sudo().form_feedback(
           post, 'iugu')
        return res