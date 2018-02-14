from openerp.osv import osv, fields

class tier(osv.osv):
	_name = 'franchisee.tier'
	_description = 'Franchisee tier'
	_columns = {
		'name': fields.char('Tier Name', size=40, required=True),
		'percentage': fields.float('Percentage', required=True),
	}

	_sql_constraints = [
		('perxentage_check_min', 'check (percentage > 0)', 'Perxentage must be more than 0 '),
		('perxentage_check_max', 'check (percentage < 100)', 'Perxentage must be less than 100'),
	]