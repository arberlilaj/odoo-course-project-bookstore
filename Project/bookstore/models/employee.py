# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BookstoreEmployee(models.Model):
    """ This model represents employee."""
    _name = 'bookstore.employee'
    _description = 'Employee'

    name = fields.Char(string='Client Name', required=True)
    surname = fields.Char(string='Surname', required=True)
    position = fields.Selection(selection=[('cashier', 'Cashier'), ('manager', 'Manager'), ('admin', 'Admin')])
    salary = fields.Float(string='Salary', digits=(12, 4))
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    hire_date = fields.Date(string='Date Hired', required=True)
    status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')])
    description = fields.Text(string='Description')

    @api.model_create_multi
    def create(self, vals):
        """Override the default create method to customize record creation logic."""
        return super().create(vals)
