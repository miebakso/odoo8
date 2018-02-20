from openerp import models, fields, api


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

	@api.onchange('is_franchisee')
	def _check_is_franchisee(self):
		if self.is_franchisee == False:
			self.tier_id = None

# ==========================================================================================================================

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	franchisee_id = fields.Many2one('res.partner','Franchisee' ,domain="[('is_franchisee','=','True')]" ,ondelete='cascade')

	@api.multi
	def invoice_validate(self):
		self.write({'state': 'open'})
		inv_obj = self.env['franchisee.bill']
		bill = inv_obj.create({
			'invoice_id': self.number,
			'customer': self.partner_id.name,
			'franchisee': self.franchisee_id.name,
			'date': self.date_invoice,
			'total_bill': self.amount_total,
			'nilai_komisi': self.amount_total * self.franchisee_id.tier_id.percentage/100
			})
		return bill

	@api.multi
	def confirm_paid(self):
		data = self.env['franchisee.bill'].search([('invoice_id', '=', self.number)])
		# data = self.env['franchisee.bill'].browse(vals.get('invoice_id', None))
		data.write({'state': 'paid'})
		self.write({'state': 'paid'})
		return data

# ==========================================================================================================================

class franchisee_bill(models.Model):
	_name = 'franchisee.bill'

	invoice_id = fields.Char('Invoice ID', required=True)
	customer = fields.Char('Customer', required=True)
	franchisee = fields.Char('Franchisee', required=True)
	date = fields.Date('Invoice Date')
	total_bill = fields.Integer('Total Price')
	nilai_komisi = fields.Integer('Nilai Komisi')
	state = fields.Selection([
		('draft','Draft'),
		('paid','Paid')],'State',default='draft')
	
	_rec_name = 'customer'


# ==========================================================================================================================
	
class res_users(models.Model):
	_inherit = 'res.users'

	franchisee_id = fields.Many2one('res.partner','Franchisee' ,domain="[('is_franchisee','=','True')]" ,ondelete='cascade')

