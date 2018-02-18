from openerp import models, fields, api


# ==========================================================================================================================

class tier(models.Model):
	_name = 'franchisee.tier'
	_description = 'Franchisee tier'
	
	name = fields.Char('Tier Name', size=40, required=True)
	percentage = fields.Float('Percentage', required=True)
	franchisee_ids = fields.One2many('res.partner','tier_id','Franchisee')
	

	_sql_constraints = [
		('percentage_check','check(percentage>0 and percentage < 100)','Percentage must be more than 0 and less than 100')
	]


# ==========================================================================================================================

class res_partner(models.Model):
	_inherit = 'res.partner'

	is_franchisee = fields.Boolean('Is Franchisee')
	tier_id = fields.Many2one('franchisee.tier','Tier', ondelete='restrict')

	@api.onchange('is_franchisee')
	def _check_is_franchisee(self):
		if self.is_franchisee == False:
			self.tier_id = False
