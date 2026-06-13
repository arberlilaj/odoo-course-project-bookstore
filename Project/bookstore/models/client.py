# -*- coding: utf-8 -*-
from odoo import api,fields, models


class BookstoreClient(models.Model):
    """ This model represents client."""
    _name = 'bookstore.client'
    _description = 'Client'

    name = fields.Char(string='Client Name', required=True)
    surname = fields.Char(string='Surname', required=True)
    client_code = fields.Char(string='Client Code')
    point = fields.Float(string='Points', digits=(16, 2))  # Foreign key from membership
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    #Te reja
    # Stores the info from the active membership
    current_tier_id = fields.Many2one('bookstore.membership.tier', string='Current Tier', readonly=True)
    membership_expiry = fields.Date(string='Membership Expires', readonly=True)
    # e re
    points_log_ids = fields.One2many('bookstore.points.log', 'client_id', string='Points History')

    is_member = fields.Boolean(compute='_compute_is_member', string='Is Active?')

    @api.depends('membership_expiry')
    def _compute_is_member(self):
        today = fields.Date.today()
        for rec in self:
            if rec.membership_expiry and rec.membership_expiry >= today:
                rec.is_member = True
            else:
                rec.is_member = False
