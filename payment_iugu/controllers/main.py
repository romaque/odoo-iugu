# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug
from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)

class OgoneController(http.Controller):
    _accept_url = '/payment/iugu/feedback'

    @http.route([
        '/payment/iugu/feedback',
    ], type='http', auth='none', csrf=False)
    def iugu_form_feedback(self, **post):
        request.registry['payment.acquirer']._create_iugu_invoice(post)
        return werkzeug.utils.redirect(post.pop('return_url', '/'))