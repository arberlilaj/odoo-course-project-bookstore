# -*- coding: utf-8 -*-
from odoo import api,fields, models


class BookstoreBookCopy(models.Model):
    _name = 'bookstore.physical.copy'
    _description = 'Physical Book Copy'
    _rec_name = 'barcode'# Display barcode in dropdowns instead of ID

    # Link to the Master Catalog (e.g., "Dune")
    book_id = fields.Many2one('bookstore.book', string='Book Title', required=True)

    # Unique ID for this specific physical item
    barcode = fields.Char(string='Barcode / Inventory ID', required=False, copy=False, readonly=True, default='New')

    # Condition/Status
    status = fields.Selection([
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('lost', 'Lost'),
        ('maintenance', 'Repairs/Damaged')
    ], default='available', string='Status')


    #store the current active loan.
    current_loan_id = fields.Many2one('bookstore.loan', string="Active Loan", readonly=True)


    current_borrower_id = fields.Many2one(
        related='current_loan_id.client_id',
        string='Borrowed By',
        store=True,
        readonly=True
    )

    @api.model
    def create(self, vals):
        # 2. Assign Sequence if barcode is missing or set to 'New'
        if vals.get('barcode', 'New') == 'New':
            vals['barcode'] = self.env['ir.sequence'].next_by_code('bookstore.physical.copy') or 'New'

        return super(BookstoreBookCopy, self).create(vals)

    def _compute_display_name(self):
        for record in self:
            # Result: "Harry Potter [INV-001]"
            if record.book_id and record.barcode:
                record.display_name = f"{record.book_id.title} [{record.barcode}]"
            else:
                record.display_name = record.barcode or "New"
    '''
   @api.depends('status')
    def _compute_borrower(self):
        for copy in self:
            copy.current_borrower_id = False
            if copy.status == 'on_loan':
                # Find the active loan for this copy
                active_loan = self.env['bookstore.loan'].search([
                    ('copy_id', '=', copy.id),
                    ('state', '=', 'active')  # Assuming 'active' is the status for ongoing loans
                ], limit=1)

                if active_loan:
                    copy.current_borrower_id = active_loan.client_id
    '''

    date_acquired = fields.Date(string='Date Acquired', default=fields.Date.today)

    _sql_constraints = [
        ('barcode_unique', 'unique(barcode)', 'This barcode already exists!')
    ]
