# -*- coding: utf-8 -*-
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class BookstoreMembership(models.Model):
    _name = 'bookstore.membership'
    _description = 'Client Membership Subscription'
    _rec_name = 'client_id'

    client_id = fields.Many2one('bookstore.client', string='Client', required=True)
    tier_id = fields.Many2one('bookstore.membership.tier', string='Tier', required=True)
    price = fields.Float(string='Price', readonly=True)

    start_date = fields.Date(string='Start Date', default=fields.Date.today, required=True)



    duration_months = fields.Integer(string='Duration (Months)', default=1, required=True)


    end_date = fields.Date(string='Expiry Date', compute='_compute_end_date', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
    ], default='draft', string='Status')


    @api.constrains('duration_months')
    def _check_duration(self):
        for rec in self:
            if rec.duration_months < 1:
                raise ValidationError("Duration must be at least 1 month.")

    @api.onchange('tier_id')
    def _onchange_tier(self):
        if self.tier_id:
            self.price = self.tier_id.price

    @api.depends('start_date', 'duration_months')
    def _compute_end_date(self):
        for rec in self:
            # Logic remains the same, but now works with any integer number
            if rec.start_date and rec.duration_months:
                rec.end_date = rec.start_date + relativedelta(months=rec.duration_months)
            else:
                rec.end_date = False

    def action_confirm(self):
        self.state = 'active'
        self.client_id.write({
            'membership_expiry': self.end_date,
            'current_tier_id': self.tier_id.id
        })

    def action_cancel(self):
        self.state = 'canceled'
        self.client_id.write({
            'membership_expiry': False,
            'current_tier_id': False
        })
