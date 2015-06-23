import requests
import json
import simplejson


APIURL = 'http://wri-01.cartodb.com/api/v2/sql'
APIKEY = '0e5365cb1a299778e9df9c7bf6db489af8aa08e1'
GFW_APIURL = 'http://beta.gfw-apis.appspot.com/forest-change'

#palm oil concessions has a field that records tree cover loss in 2013 (loss_in_2013)

#A table that links each district to its concessions: https://wri-01.cartodb.com/tables/district_palm_table
#A table that links each district to its HP and HPT areas

#risk indictor 1
def loss_in_illegal(district_id):
	perc = loss_in_


#protected area has fields that record tree cover loss in 2001-2013, sum of loss from 2001-2013, and fields that record the change rate from 2009-2013

#risk indictor 2:
#a talbe that links each district to its protected area
def loss_in_protected(cartodb_id, intersec_table):
	query = """
			SELECT %s FROM %s
			WHERE %s = %d""" % (id_fieldname, table)

	protected_area = sum_area(polygon_id,idfieldname, district_id,table) 

	loss_in_protected = get_the_loss(district_id, intersec_table)
	perc = loss_in_protected/protected_area
	return perc

def rate_loss_in_protected(district_id, intersec_table):
	return

def update_table(table, field, value, identifier, id_fieldname):
	query = """
			UPDATE %s SET %s = %f
			WHERE %s = %d""" % (table,field, value, id_fieldname, identifier)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))


def get_all_ids(table, id_fieldname):	
	query = """
			SELECT %s FROM %s""" % (id_fieldname, table)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
	id_list = r.json()['rows']
	return id_list

def get_geoms(intersect_id, id_fieldname, table):
    query = """
            SELECT the_geom FROM %s
    		WHERE %s = '%s'""" % (table, id_fieldname, intersect_id)

    r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query, format='geojson'))

    geoms = r.json()['features'][0]['geometry']
    strgeom = json.dumps(geoms)
    return strgeom

def gfw_api_request(geom, start_date, end_date, dataset, threshold=30):
    """Make GFW API request for a given geom to calculate the loss in a
    given area."""
    if geom == 'null' or not geom:
        return 0
    p = '%s,%s' % (start_date, end_date)
    params = dict(period=p, geojson=geom, threshold=threshold)
    url = '%s/%s' % (GFW_APIURL, dataset)
    r = requests.post(url, data=params)


    try:
        if dataset == 'umd-loss-gain':
            loss = r.json()['loss']
        elif dataset == 'forma-alerts':
            loss = r.json()['value']
        elif dataset == 'nasa-active-fires':
            loss = r.json()['value']
        return loss
    except simplejson.scanner.JSONDecodeError:
        print r.content
        exit

def sum_area(polygon_id,idfieldname, district_id,table):
	total_area = 0
	for ids in palm_ids:
		palm_id = ids['palm_id']
		query = """
				SELECT area_hectare FROM %s
				WHERE %s = '%s'""" % (table, idfieldname, district_id)
		r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
		area = r.json()['rows'][0]['area_hectare']
		total_area = total_area + area
	return total_area

def loss_in_protect(start_date, end_date, d):
	table = 'idn_adm2_protected'
	id_fieldname = 'intersect_id'
	ids = get_all_ids(table, id_fieldname)
	orange = 0
	for intersection in ids:
		intersect_id = intersection['intersect_id']
		print intersect_id
		if orange <= 587:
			orange+=1
			continue
		else:
			geom = get_geoms(intersect_id, id_fieldname, table)
			dataset = 'umd-loss-gain'
		
			loss = gfw_api_request(geom, start_date, end_date, dataset, threshold=30)
			loss_field = 'loss_%s'% d
			print loss_field
			print loss
			update_table(table, loss_field, loss, intersect_id, id_fieldname)
			print orange
			orange+=1


def main():
	start_dates = []
	end_dates = []
	i = 1
	while(i <= 13):
		c = str(2000 + i)
		d = str(2000 + i + 1)
		start_date = '%s-01-01' % c
		end_date = '%s-01-01' % d
		loss_in_protect(start_date, end_date, c)
		i+=1