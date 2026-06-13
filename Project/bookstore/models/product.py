# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    """ This model represents product."""
    _name = 'bookstore.product'
    _description = 'Product'
    _rec_name = 'product'

    product = fields.Char(string='Product name', required=True)
    quantity = fields.Float(string='Quantity', digits=(16, 6), default=0)
    purchase_price = fields.Float(string='Purchase price', digits=(12, 4))
    sell_price = fields.Float(string='Sell price', digits=(12, 4))
    category_ids = fields.Many2many(comodel_name='bookstore.category', string='')
    #Te reja
    is_membership = fields.Boolean(string='For members only', default=False)
    membership_days = fields.Integer(string='Duration (Days)', default=30)
    # e re
    type = fields.Selection([
        ('product', 'Storable Product'),  # Books, Cans (Track Stock)
        ('service', 'Service / Consumable')  # Coffee, Juice (Don't Track Stock)
    ], string='Product Type', default='product', required=True)

    material_ids = fields.One2many('bookstore.product.material', 'parent_product_id', string="Ingredients")

    @api.constrains('quantity')
    def _check_quantity(self):
        for product in self:
            if product.quantity < 0:
                raise ValidationError(f'Quantity must be positive, {product.product}: {product.quantity}')

    #Te reja nr2
    book_id = fields.Many2one('bookstore.book', string='Master Book')
    @api.onchange('book_id')
    def _onchange_book_id(self):
        if self.book_id:
            # Sets name to "Title - Author"
            self.name = f"{self.book_id.title} - {self.book_id.author}"


class BookstoreMaterial(models.Model):
    _name = 'bookstore.product.material'
    _description = 'Ingredients'

    parent_product_id = fields.Many2one('bookstore.product', string="Parent Product")

    # Only show Storable products (Type = Product) in the dropdown
    ingredient_id = fields.Many2one('bookstore.product', string="Ingredient",
                                    domain="[('type', '=', 'product')]", required=True)

    quantity = fields.Float(string="Qty Needed", default=1.0)
class BookstoreCategory(models.Model):
    _name = 'bookstore.category'
    _rec_name = 'category'

    category = fields.Char(string='Category name')
