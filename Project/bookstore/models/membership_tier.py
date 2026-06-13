# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import fields, models

class BookstoreMembershipTier(models.Model):
    _name = 'bookstore.membership.tier'
    _description = 'Membership Tier'

    name = fields.Char(string='Tier Name', required=True) # e.g. "Gold"
    price = fields.Float(string='Standard Price', required=True)
    description = fields.Text(string='Description')
