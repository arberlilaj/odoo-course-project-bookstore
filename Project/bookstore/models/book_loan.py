from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class BookstoreLoan(models.Model):
    _name = 'bookstore.loan'
    _description = 'Book Loan Transaction'

    client_id = fields.Many2one('bookstore.client', string="Client", required=True)
    employee_id = fields.Many2one('bookstore.employee', string="Employee", help="Who processed this loan")

    # select title
    book_id = fields.Many2one('bookstore.book', string="Book Title", required=True)

    # Domain filters based on the selected book_id
    physical_copy_id = fields.Many2one('bookstore.physical.copy', string="Physical Copy (Barcode)", required=True,
                                       # show copy's that are for the specific book & available
                                       domain="[('book_id', '=', book_id), ('status', '=', 'available')]"
                                       )


    date_borrowed = fields.Date(default=fields.Date.today, required=True)
    duration_days = fields.Integer(string="Duration (Days)", default=7)
    due_date = fields.Date(compute='_compute_due_date', store=True)
    date_returned = fields.Date(string="Date Returned", readonly=True)

    # bookstore.book has a currency_id, otherwise remove currency_field logic
    currency_id = fields.Many2one('res.currency', related='physical_copy_id.book_id.currency_id')
    total_cost = fields.Monetary(compute='_compute_cost', store=True, currency_field='currency_id')

    # link invoice
    invoice_id = fields.Many2one('bookstore.invoice', string="Invoice", readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('returned', 'Returned'),
    ], default='draft')



    # If a book is selected the copy is reseted for that book
    @api.onchange('book_id')
    def _onchange_book_id(self):
        # When Book changes, clear the Copy field
        self.physical_copy_id = False

    @api.depends('date_borrowed', 'duration_days')
    def _compute_due_date(self):
        for record in self:
            if record.date_borrowed and record.duration_days:
                record.due_date = record.date_borrowed + relativedelta(days=record.duration_days)

    @api.depends('duration_days', 'physical_copy_id')
    def _compute_cost(self):
        for record in self:
            rate = record.physical_copy_id.book_id.rental_price_per_day
            record.total_cost = record.duration_days * rate

    # --- ACTIONS ---

    def action_confirm_loan(self):
        for loan in self:
            if loan.physical_copy_id.status != 'available':
                raise ValidationError("This book is not available!")

            loan.state = 'active'
            loan.physical_copy_id.status = 'on_loan'
            loan.physical_copy_id.current_loan_id = loan.id

    def action_return_book(self):
        for loan in self:
            loan.state = 'returned'
            loan.date_returned = fields.Date.today()
            loan.physical_copy_id.status = 'available'
            loan.physical_copy_id.current_loan_id = False

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'bookstore.invoice',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
        }
    def action_create_invoice(self):
        """ Generates a bookstore.invoice from this loan """
        self.ensure_one()
        if self.invoice_id:
            raise UserError("Invoice already created!")




        rental_product = self.env['bookstore.product'].search([('product', '=', 'Rental Service')], limit=1)

        if not rental_product:
            raise UserError(
                "Please create a product named 'Rental Service' in Bookstore Products to use for invoicing loans.")

        # 1. Create Invoice Header
        invoice_vals = {
            'invoice_type': 'out',  # Sell
            'client_id': self.client_id.id,
            'employee_id': self.employee_id.id or self.env.user.employee_id.id,
            'state': 'draft',
        }
        invoice = self.env['bookstore.invoice'].create(invoice_vals)

        # 2. Create Invoice Line
        # We override the price with our computed total_cost
        line_vals = {
            'invoice_id': invoice.id,
            'product_id': rental_product.id,
            'quantity': 1,
            'price': self.total_cost,
        }
        self.env['bookstore.invoice.line'].create(line_vals)

        # 3. Link and Open
        self.invoice_id = invoice.id

        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'bookstore.invoice',
            'res_id': invoice.id,
            'view_mode': 'form',
        }
