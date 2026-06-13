# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class SalesStatisticsWizard(models.TransientModel):
    """
    Wizard for generating sales statistics report.
    """
    _name = 'bookstore.sales.statistics.wizard'
    _description = 'Sales Statistics Report Wizard'

    # Date range fields for filtering
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)  # First day of current month
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )

    # Optional filters
    client_id = fields.Many2one(
        'bookstore.client',
        string='Filter by Client',
        help='Leave empty to include all clients'
    )
    employee_id = fields.Many2one(
        'bookstore.employee',
        string='Filter by Employee',
        help='Leave empty to include all employees'
    )
    invoice_type = fields.Selection([
        ('all', 'All Transactions'),
        ('in', 'Purchases Only'),
        ('out', 'Sales Only'),
    ], string='Transaction Type', default='out', required=True)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate that date_from is before or equal to date_to"""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError('From Date must be before or equal to To Date!')

    def _get_report_data(self):
        """
        Gathers and calculates all the statistics data for the report.
        Returns a dictionary with the report data.
        """
        self.ensure_one()

        # Build domain for searching invoices
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', 'in', ['done', 'paid']),  # Only confirmed invoices
        ]

        # Apply optional filters
        if self.client_id:
            domain.append(('client_id', '=', self.client_id.id))
        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))
        if self.invoice_type != 'all':
            domain.append(('invoice_type', '=', self.invoice_type))

        # Fetch invoices
        invoices = self.env['bookstore.invoice'].search(domain, order='invoice_date')

        # Calculate statistics
        total_sales = sum(inv.total for inv in invoices if inv.invoice_type == 'out')
        total_purchases = sum(inv.total for inv in invoices if inv.invoice_type == 'in')
        total_transactions = len(invoices)

        # Top selling products
        product_sales = {}
        for invoice in invoices:
            if invoice.invoice_type == 'out':
                for line in invoice.invoice_line_ids:
                    product_name = line.product_id.product
                    if product_name in product_sales:
                        product_sales[product_name]['qty'] += line.quantity
                        product_sales[product_name]['total'] += line.total
                    else:
                        product_sales[product_name] = {
                            'qty': line.quantity,
                            'total': line.total
                        }

        # Sort products by total sales and get top 10
        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:10]

        # Sales by client
        client_sales = {}
        for invoice in invoices:
            if invoice.invoice_type == 'out' and invoice.client_id:
                client_name = f"{invoice.client_id.name} {invoice.client_id.surname}"
                if client_name in client_sales:
                    client_sales[client_name] += invoice.total
                else:
                    client_sales[client_name] = invoice.total

        # Sort clients by total spending
        top_clients = sorted(
            client_sales.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'wizard': self,
            'invoices': invoices,
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'total_transactions': total_transactions,
            'profit': total_sales - total_purchases,
            'top_products': top_products,
            'top_clients': top_clients,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

    def action_print_report(self):
        """
        Action to generate and print the sales statistics PDF report.
        Called when user clicks the 'Print Report' button in the wizard.
        """
        self.ensure_one()
        return self.env.ref('bookstore.action_report_sales_statistics').report_action(self)

    def action_view_invoices(self):
        """
        Action to view the filtered invoices in a list view.
        Alternative action for those who want to see raw data.
        """
        self.ensure_one()

        # Build domain for searching invoices
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', 'in', ['done', 'paid']),
        ]

        if self.client_id:
            domain.append(('client_id', '=', self.client_id.id))
        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))
        if self.invoice_type != 'all':
            domain.append(('invoice_type', '=', self.invoice_type))

        return {
            'name': 'Filtered Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'bookstore.invoice',
            'view_mode': 'tree,form',
            'domain': domain,
            'target': 'current',
        }
