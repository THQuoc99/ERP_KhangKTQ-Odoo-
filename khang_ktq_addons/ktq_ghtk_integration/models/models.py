# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ktq_ghtk_integration(models.Model):
#     _name = 'ktq_ghtk_integration.ktq_ghtk_integration'
#     _description = 'ktq_ghtk_integration.ktq_ghtk_integration'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

