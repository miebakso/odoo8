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

	is_franchisee = fields.Boolean('Is Franchisee')
	tier_id = fields.Many2one('franchisee.tier', 'Tier', ondelete='restrict')
	invoice_ids = fields.One2many('account.invoice','franchisee_id','Invoice')
	customers = fields.One2many('franchisee.bill', 'customer', 'Customer')
	# franchisees = fields.One2many('franchisee.bill', 'franchisee', 'Franchisee')

	@api.onchange('is_franchisee')
	def _check_is_franchisee(self):
		if self.is_franchisee == False:
			self.tier_id = None

# ==========================================================================================================================

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	franchisee_id = fields.Many2one('res.partner','Franchisee' ,domain="[('is_franchisee','=','True')]" ,ondelete='cascade')
	invoice_ids = fields.One2many('franchisee.bill', 'invoice_id', 'Franchisee Bill')

	@api.constrains('partner_id')
	def _check_partner_id(self):
		for record in self:
			if record.partner_id.is_franchisee == True:
				raise ValidationError('This customer is franchisee')

	@api.multi
	def invoice_validate(self):
		for record in self:
			record.write({'state': 'open'})
			inv_obj = record.env['franchisee.bill']
			bill = inv_obj.create({
				'invoice_id': record.id,
				'customer': record.id,
				'franchisee': record.franchisee_id.name,
				'date': record.date_invoice,
				'total_bill': record.amount_total,
				'total_discount': record.amount_total * record.franchisee_id.tier_id.percentage/100
				})
			return bill

	@api.multi
	def confirm_paid(self):
		data = self.env['franchisee.bill'].search([('invoice_id', '=', self.number)])
		# data = self.env['franchisee.bill'].browse(vals.get('invoice_id', None))
		data.write({'state': 'paid'})
		self.write({'state': 'paid'})
		return data

		
	# @api.multi
	# def _compute_discount(self):
	# 	for record in self:
	# 		record.total_bill = record.amount_total * record.franchisee_id.tier_id.percentage/100


# ==========================================================================================================================

class franchisee_bill(models.Model):
	_name = 'franchisee.bill'
	_description = 'Franchisee Bill'

	# invoice_id = fields.Char('Invoice ID', required=True)
	invoice_id = fields.Many2one('account.invoice', 'Invoice ID', ondelete='cascade')
	# customer = fields.Char('Customer', required=True)
	customer = fields.Many2one('res.partner', 'Customer', ondelete='cascade')
	# franchisee = fields.Char('Franchisee', required=True)
	franchisee = fields.Many2one('res.partner', 'Franchisee', domain="[('is_franchisee','=','True')]", ondelete='cascade')
	date = fields.Date('Invoice Date')
	total_bill = fields.Float('Total Price')
	total_discount = fields.Float('Total Discount')
	state = fields.Selection([
		('draft','Draft'),
		('paid','Paid')],'State',default='draft')
	
	_rec_name = 'customer'

# ==========================================================================================================================
	
class res_users(models.Model):
	_inherit = 'res.users'

	franchisee_id = fields.Many2one('res.partner','Franchisee' ,domain="[('is_franchisee','=','True')]" ,ondelete='cascade')

