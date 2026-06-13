# -*- coding: utf-8 -*-
from odoo import api,fields, models


# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BookstoreBook(models.Model):
    _name = 'bookstore.book'
    _description = 'Book Catalog Data'
    _rec_name = 'title'

    # Essential Data
    title = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author', required=True)
    isbn = fields.Char(string='ISBN', required=True, copy=False)
    genre = fields.Char(string='Genre', required=True, placeholder="e.g. Sci-Fi, Thriller")

    # Details
    publisher = fields.Char(string='Publisher')
    year_published = fields.Integer(string='Year')


    # Loan Cost Calculation
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    retail_price = fields.Monetary(string="Retail Price", currency_field='currency_id')
    rental_price_per_day = fields.Monetary(string="Rental Price / Day", default=0.50, currency_field='currency_id')

    # 1. Link to the physical copies
    copy_ids = fields.One2many('bookstore.physical.copy', 'book_id', string='Physical Copies')

    # 2. Computed Counts
    total_copies_count = fields.Integer(string='Total Copies', compute='_compute_counts')
    available_copies_count = fields.Integer(string='Available', compute='_compute_counts')

    # Location
    shelf_location = fields.Char(string='Shelf Location', default="A-1", help="e.g. A-3")

    _sql_constraints = [
        ('isbn_unique', 'unique(isbn)', 'This ISBN already exists in the system!')
    ]

    @api.depends('copy_ids.status')
    def _compute_counts(self):
        for book in self:
            book.total_copies_count = len(book.copy_ids)
            book.available_copies_count = len(book.copy_ids.filtered(lambda c: c.status == 'available'))
