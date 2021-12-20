# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.translate import html_translate


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    website_description = fields.Html(
        'Website Description', sanitize_attributes=False, translate=html_translate, sanitize_form=False,
        compute='_compute_website_description', store=True, readonly=False)

    @api.depends('partner_id', 'sale_order_template_id')
    def _compute_website_description(self):
        for order in self:
            if not order.sale_order_template_id:
                continue
            template = order.sale_order_template_id.with_context(lang=order.partner_id.lang)
            order.website_description = template.website_description

    def _compute_line_data_for_template_change(self, line):
        vals = super(SaleOrder, self)._compute_line_data_for_template_change(line)
        vals.update(website_description=line.website_description)
        return vals

    def _compute_option_data_for_template_change(self, option):
        vals = super(SaleOrder, self)._compute_option_data_for_template_change(option)
        vals.update(website_description=option.website_description)
        return vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    website_description = fields.Html('Website Description', sanitize=False, translate=html_translate, sanitize_form=False)

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._inject_quotation_description(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, values):
        values = self._inject_quotation_description(values)
        return super().write(values)

    def _inject_quotation_description(self, values):
        values = dict(values or {})
        if not values.get('website_description') and values.get('product_id'):
            product = self.env['product.product'].browse(values['product_id'])
            values.update(website_description=product.quotation_description)
        return values


class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    website_description = fields.Html(
        'Website Description', sanitize_attributes=False, translate=html_translate,
        compute='_compute_website_description', store=True, readonly=False, precompute=True)

    @api.depends('product_id', 'uom_id')
    def _compute_website_description(self):
        for option in self:
            if not option.product_id:
                continue
            product = option.product_id.with_context(lang=option.order_id.partner_id.lang)
            option.website_description = product.quotation_description

    def _get_values_to_add_to_order(self):
        values = super(SaleOrderOption, self)._get_values_to_add_to_order()
        values.update(website_description=self.website_description)
        return values
