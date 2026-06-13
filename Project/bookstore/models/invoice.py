# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta


class BookstoreInvoice(models.Model):
    """ This model represents invoice."""
    _name = 'bookstore.invoice'

    invoice_code = fields.Char(string='Invoice Number', required=True, default='New')
    invoice_date = fields.Datetime(string='Invoice date', default=lambda self: fields.Datetime.now())
    invoice_type = fields.Selection([
        ('in', 'Purchase'),
        ('out', 'Sell')
    ], string='Status', default='out', required=True)
    client_id = fields.Many2one(comodel_name='bookstore.client', string='Client')
    employee_id = fields.Many2one(comodel_name='bookstore.employee', string='Employee')
    total = fields.Float(string='', digits=(16, 4), compute='_calc_total', store=True)
    invoice_line_ids = fields.One2many(comodel_name='bookstore.invoice.line', inverse_name='invoice_id',
                                       string='Invoice Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid'),
    ], string='Status', default='draft', required=True)

    @api.depends('invoice_line_ids')
    def _calc_total(self):
        for rec in self:
            # s = 0
            # for line in rec.invoice_line_ids:
            #     s += line.total
            # self.total = s
            rec.total = sum(self.invoice_line_ids.mapped('total'))

    @api.model
    def create(self, values):
        if values.get('invoice_type') == 'out':
            code = self.env['ir.sequence'].next_by_code('out.invoice.cp')
        else:
            code = self.env['ir.sequence'].next_by_code('in.invoice.cp')
        values['invoice_code'] = code
        res = super(BookstoreInvoice, self).create(values)
        return res

    def write(self, values):
        test = self
        res = super(BookstoreInvoice, self).write(values)
        test = self
        return res

    def unlink(self):
        for invoice in self:
            if invoice.state != 'draft':
                raise UserError('Invoice can not be deleted')
        res = super(BookstoreInvoice, self).unlink()
        return res

    def confirm_invoice(self):
        self.state = 'done'

        if self.invoice_type == 'in':
            # purchase from supplier
            for invoice_line in self.invoice_line_ids:
                #increas stock for bought items
                invoice_line.product_id.quantity += invoice_line.quantity
        else:
            # sell for client
            for invoice_line in self.invoice_line_ids:
                # Dec stock
                if invoice_line.product_id.type == 'product':
                    # Check if we have enough
                    if invoice_line.product_id.quantity < invoice_line.quantity:
                        raise UserError(f"Not enough stock for {invoice_line.product_id.product}!")
                    invoice_line.product_id.quantity -= invoice_line.quantity

                # Check if a prod is for members
                if invoice_line.product_id.is_membership:
                    self._activate_membership(invoice_line.product_id.membership_days)

            self._calculate_points()
            '''        else:
            # sell for client
            for invoice_line in self.invoice_line_ids:
                # Dec stock
                invoice_line.product_id.quantity -= invoice_line.quantity

                # Check if a prod is for members
                if invoice_line.product_id.is_membership:
                    self._activate_membership(invoice_line.product_id.membership_days)

            self._calculate_points()'''
    def _activate_membership(self, days):
        #Calc the expireed date of client

        if not self.client_id:# Cannot give membership when a client is not selected
            return

        today = fields.Date.today()

        current_expiry = self.client_id.membership_expiry


        if current_expiry and current_expiry >= today:
            new_date = current_expiry + timedelta(days=days)
        else:
            new_date = today + timedelta(days=days)

        # Write the new date to the client record
        self.client_id.write({'membership_expiry': new_date})

    def _calculate_points(self):
        """ Calculates points based on total amount and adds to client """
        if not self.client_id:
            return

        # Conversion ratee
        # Ex: 0.10 means 10% of the price becomes points
        # If Total is 1000 Leke, they get 100 Points
        conversion_rate = 0.10

        points_earned = self.total * conversion_rate

        if points_earned > 0:
            # Update client point balacne
            self.client_id.point += points_earned

    def pay_invoice(self):
        self.state = 'paid'


class BookstoreInvoiceLine(models.Model):
    _name = 'bookstore.invoice.line'

    product_id = fields.Many2one(comodel_name='bookstore.product', string='Product')
    invoice_id = fields.Many2one(comodel_name='bookstore.invoice', string='Invoice', ondelete='cascade')
    quantity = fields.Float(string='Quantity', digits=(16, 4), default=1)
    price = fields.Float(string='Price', digits=(16, 2))
    total = fields.Float(string='Total', digits=(16, 2), compute='_calc_total')

    _sql_constraints = [
        ('quantity', 'CHECK(quantity>=0)', 'Quantity must be positive'),
    ]

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.invoice_id.invoice_type == 'in':
            self.price = self.product_id.purchase_price
        else:
            self.price = self.product_id.sell_price

    @api.depends('price', 'quantity')
    def _calc_total(self):
        for rec in self:
            rec.total = rec.price * rec.quantity
