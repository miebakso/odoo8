from openerp import models, fields, api
from openerp.exceptions import ValidationError


# ==========================================================================================================================

class franchisee_tier(models.Model):
	_name = 'franchisee.tier'
	_description = 'Franchisee tier'
	
	name = fields.Char('Tier Name', size=40, required=True)
	percentage = fields.Float('Percentage', required=True)
	franchisee_ids = fields.One2many('res.partner', 'tier_id', 'Franchisee')
	

	_sql_constraints = [
		('percentage_check','CHECK(percentage>0 AND percentage < 100)','Percentage must be more than 0 and less than 100')
	]


# ==========================================================================================================================

class res_partner(models.Model):
	_inherit = 'res.partner'

	is_franchisee = fields.Boolean('Franchisee?')
	tier_id = fields.Many2one('franchisee.tier', 'Tier', ondelete='restrict')

	@api.onchange('is_franchisee')
	def onchange_franchisee(self):
		if self.is_franchisee == False:
			self.tier_id = None

# ==========================================================================================================================

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	franchisee_id = fields.Many2one('res.partner','Franchisee' ,domain="[('is_franchisee','=','True')]" ,ondelete='cascade')

	@api.constrains('partner_id')
	def _check_partner_id(self):
		for record in self:
			if record.partner_id.is_franchisee == True:
				raise ValidationError('This partner is franchisee.')

	@api.multi
	def invoice_validate(self):
		result = super(account_invoice, self).invoice_validate()
		bill_obj = self.env['franchisee.bill']
		for record in self:
			if not record.franchisee_id: continue
			lines = []
			
			bill = bill_obj.create({
				'invoice_id': record.id,
				'customer_id': record.partner_id.id,
				'franchisee_id': record.franchisee_id.id,
				'bill_date': record.date_invoice,
				'bill_lines': lines,
			    'total_bill': record.amount_untaxed,
				})

			for invoice_line in record.invoice_line:
				lines.append([0,False,{
					'bill_id': bill.id,
					'product_id': invoice_line.product_id.id,
					'qty': invoice_line.quantity,
					'unit_price': invoice_line.price_unit,
					'discount_amount': record.franchisee_id.tier_id.percentage / 100.0 * invoice_line.price_unit * invoice_line.quantity,
					# 'discount_amount': record.franchisee_id.tier_id.percentage / 100.0 * invoice_line.price_unit,
					'subtotal_per_unit': (invoice_line.price_unit*invoice_line.quantity) - (record.franchisee_id.tier_id.percentage / 100.0 *invoice_line.price_unit* invoice_line.quantity)
					}])
			bill.write({'bill_lines': lines})
		return result

	@api.multi
	def confirm_paid(self):
		result = super(account_invoice, self).confirm_paid()
		for record in self:
			data = record.env['franchisee.bill'].search([('invoice_id', '=', record.id)])
			data.write({'state': 'paid'})
		return result

# ==========================================================================================================================

class franchisee_bill(models.Model):
	_name = 'franchisee.bill'
	_description = 'Franchisee Bill'

	invoice_id = fields.Many2one('account.invoice', 'Invoice', ondelete='cascade')
	customer_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade')
	franchisee_id = fields.Many2one('res.partner', 'Franchisee', domain=[('is_franchisee','=','True')], ondelete='cascade')
	bill_date = fields.Date('Bill Date')
	bill_lines = fields.One2many('franchisee.bill.line', 'bill_id','Bill line')
	total_bill = fields.Float('Total Price')
	total_discount = fields.Float('Total Discount', compute="_compute_total")
	total_price_discount = fields.Float('TOTAL BILL', compute="_compute_total")
	state = fields.Selection([
		('draft','Draft'),
		('paid','Paid'),
		], 'State', default='draft')
	
	
	@api.multi
	def _compute_total(self):
		for record in self:
			record.total_discount = record.total_bill * record.franchisee_id.tier_id.percentage/100
			record.total_price_discount = record.total_bill - (record.total_bill * record.franchisee_id.tier_id.percentage/100)

# ==========================================================================================================================
	
class franchisee_bill_line(models.Model):

	_name = 'franchisee.bill.line'
	_description = 'Bill line'

	bill_id = fields.Many2one('franchisee.bill', 'Bill', ondelete="cascade")
	product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='restrict', index=True)
	qty = fields.Float('Qty', required=True)
	unit_price = fields.Float('Unit Price',required=True)
	# discount_amount = fields.Float('Discount Per Unit')
	discount_amount = fields.Float('Discount Per Unit', compute='_compute_total')
	subtotal_per_unit = fields.Float('Subtotal')
	total = fields.Float('Total', compute='_compute_total')

	# @api.multi
	# def _compute_total(self):
	# 	for record in self:
	# 		record.discount_amount = record.unit_price * record.bill_id.franchisee_id.tier_id.percentage/100
	# 		# record.subtotal = record.discount_amount * record.qty
	@api.multi
	def _compute_total(self):
		for record in self:
			record.discount_amount = record.unit_price * record.bill_id.franchisee_id.tier_id.percentage/100
			record.total = record.discount_amount * record.qty
			
	
# ==========================================================================================================================
	
class res_users(models.Model):
	_inherit = 'res.users'

	franchisee_id = fields.Many2one('res.partner','Franchisee' ,domain="[('is_franchisee','=','True')]" ,ondelete='cascade')
