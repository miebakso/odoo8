from openerp.osv import osv, fields


# ==========================================================================================================================

class tier(osv.osv):
	_name = 'franchisee.tier'
	_description = 'Franchisee tier'
	_columns = {
		'name': fields.char('Tier Name', size=40, required=True),
		'percentage': fields.float('Percentage', required=True),
		'franchisee_ids': fields.one2many('franchisee.franchisee','tier_id','Franchisee'),
	}

	_sql_constraints = [
		('percentage_check','check(percentage>0 and percentage < 100)','Percentage must be more than 0 and less than 100')
	]


# ==========================================================================================================================

class franchisee(osv.osv):
	_name = 'franchisee.franchisee'
	_description = 'Franchisee User'

	_inherit = 'res.partner'

	_columns = {
		'tier_id': fields.many2one('franchisee.tier','Tier', ondelete='restrict'),
	}
