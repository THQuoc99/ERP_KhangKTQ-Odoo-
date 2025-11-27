# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Thêm trường để lưu GHTK Token
    # 'config_parameter' báo Odoo lưu giá trị này vào hệ thống
    ktq_ghtk_api_token = fields.Char(
        string="GHTK API Token",
        config_parameter='ktq_ghtk_integration.api_token'
    )