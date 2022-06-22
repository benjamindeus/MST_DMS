from odoo import models, fields, api, _


class GeneralAdvance(models.Model):

    _name = 'general.advance'
    _description = 'General Advance'

    item_description = fields.Char(
        string='Item Description',
    )

    price = fields.Float(
        string='Price',
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='UOM',
    )

    qty = fields.Float(
        string='Quantity',
    )

    sub_total = fields.Float(
        string='Sub Total',
    )

    imprest_id = fields.Many2one(
        'imprest.application',
        string='Application',
    )

    @api.onchange('qty', 'price')
    def _onchange_unit_price(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.price
