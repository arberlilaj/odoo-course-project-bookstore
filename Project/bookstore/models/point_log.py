# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BookstorePointLog(models.Model):
    """ This model represents point.log."""
    _name = 'bookstore.points.log'
    _description = 'Points History'


    client_id = fields.Many2one('bookstore.client', string='Client', required=True)
    points_change = fields.Float(string='Points Changed', required=True)
    #reason = fields.Char(string='Reason')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
