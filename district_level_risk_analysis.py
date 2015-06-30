import requests
import json
import simplejson
import numpy
 
 
APIURL = 'http://wri-01.cartodb.com/api/v2/sql'
APIKEY = '0e5365cb1a299778e9df9c7bf6db489af8aa08e1'
GFW_APIURL = 'http://staging.gfw-apis.appspot.com/forest-change'
 
 
 
#protected area has fields that record tree cover loss in 2001-2013, sum of loss from 2001-2013, and fields that record the change rate from 2009-2013
 
 
 
def summarize_loss_in_intersec(intersec_table, FieldOfInterest, FieldInRiskTable):
	n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
	for id_2 in range(1,n+1):
		print id_2
		intersect_area_list = get_intersect_values(intersec_table,'area_hectare','adm_id', id_2)
		if len(intersect_area_list)==0:
			continue
		else:
			total_intersect_area = sum_value(intersect_area_list)
 
			intersect_FieldOfInterest = get_intersect_values(intersec_table, FieldOfInterest, 'adm_id', id_2)
			total_FieldOfInterest = sum_value(intersect_FieldOfInterest)
			perc = total_FieldOfInterest/total_intersect_area
		print perc
		
		update_table('idn_adm2_risk_analysis', FieldInRiskTable, perc,id_2, 'id_2')
 
def rate_loss_in_protected():
	intersec_table = 'idn_adm2_protected'
	n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
	for id_2 in range(1,n+1):
		print id_2
		intersect_area_list = get_intersect_values(intersec_table,'area_hectare','adm_id', id_2)
		if len(intersect_area_list)==0:
			continue
		else:
			total_protected_area = sum_value(intersect_area_list)
 
			"""Calculate tree cover loss in protected areas in 2009-2013"""
 
			intersect_loss_2008_list = get_intersect_values(intersec_table, 'loss_2008', 'adm_id', id_2)
			total_loss_2008 = sum_value(intersect_loss_2008_list)
 
			intersect_loss_2009_list = get_intersect_values(intersec_table, 'loss_2009', 'adm_id', id_2)
			total_loss_2009 = sum_value(intersect_loss_2009_list)
 
			intersect_loss_2010_list = get_intersect_values(intersec_table, 'loss_2010', 'adm_id', id_2)
			total_loss_2010 = sum_value(intersect_loss_2010_list)
 
			intersect_loss_2011_list = get_intersect_values(intersec_table, 'loss_2011', 'adm_id', id_2)
			total_loss_2011 = sum_value(intersect_loss_2011_list)
 
			intersect_loss_2012_list = get_intersect_values(intersec_table, 'loss_2012', 'adm_id', id_2)
			total_loss_2012 = sum_value(intersect_loss_2012_list)
 
			intersect_loss_2013_list = get_intersect_values(intersec_table, 'loss_2013', 'adm_id', id_2)
			total_loss_2013 = sum_value(intersect_loss_2013_list)
 
			try:
 
				change_rate09 = (total_loss_2009-total_loss_2008)/total_loss_2008
			
				change_rate10 = (total_loss_2010-total_loss_2009)/total_loss_2009
			
				change_rate11 = (total_loss_2011-total_loss_2010)/total_loss_2010
			
				change_rate12 = (total_loss_2012-total_loss_2011)/total_loss_2011
			
				change_rate13 = (total_loss_2013-total_loss_2012)/total_loss_2012
 
				avg_change_rate = numpy.mean([change_rate09, change_rate10, change_rate11, change_rate12, change_rate13])
				update_table('idn_adm2_risk_analysis', 'rate_of_loss_in_protected_areas', avg_change_rate, id_2,'id_2')
 
			except ZeroDivisionError:
				continue
 
def palm_concession_in_protected(intersec_table,overlapping_table,FieldOfInterest,FieldInRiskTable):
	
	n = 441
	for id_2 in range(1,n+1):
		print id_2
		intersect_area_list = get_intersect_values(intersec_table,'area_hectare','adm_id', id_2)
		if len(intersect_area_list)==0:
			continue
		else:
			total_intersec_area = sum_value(intersect_area_list)
			overlapping_area_list = get_intersect_values(overlapping_table,FieldOfInterest,'adm_id', id_2)
			try:
				total_overlapping_area = sum_value(overlapping_area_list)
				perc = total_overlapping_area/total_intersec_area
				update_table('idn_adm2_risk_analysis', FieldInRiskTable, perc, id_2,'id_2')
 
 
			except ZeroDivisionError:
					continue
 
def update_table(table, field, value, identifier, id_fieldname):
	query = """
			UPDATE %s SET %s = %f
			WHERE %s = %d""" % (table,field, value, id_fieldname, identifier)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
 
 
def get_intersect_values(table, fieldname, where_name, where_value):	
	query = """
			SELECT %s FROM %s where %s = %s""" % (fieldname, table, where_name, where_value)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
	value_list = r.json()['rows']
	return value_list
 
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
 
def get_simple_geoms(intersect_id, id_fieldname, table):
    
    query = """
        	SELECT ST_Simplify(the_geom::geometry, 0.1)the_geom
        	FROM %s
       		WHERE %s = '%s'""" % (table, id_fieldname, intersect_id)
 
    r = requests.get(
        APIURL, params=dict(api_key=APIKEY, q=query, format='geojson'))
   
    try:
        
        geoms = r.json()['features'][0]['geometry']
        strgeom = json.dumps(geoms)
        return strgeom
    except IndexError:
        
        return None
 
def sum_value(valuelist):
	total_value = 0
	for next_value in valuelist:
		value = next_value.values()[0]
		total_value += value
	return total_value
 
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
 
def sum_values(polygon_id,idfieldname, district_id,table):
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
 
def loss_in_geom(table, start_date, end_date, d):
	#table = 'idn_adm2_protected'
	id_fieldname = 'intersect_id'
	
	ids = get_all_ids(table, id_fieldname)
	orange = 0
	for intersection in ids:
		intersect_id = intersection['intersect_id']
		print intersect_id
		if intersect_id <= 42 or intersect_id>=44:
			orange+=1
			continue
		else:
			#geom = get_geoms(intersect_id, id_fieldname, table)
			geom = get_simple_geoms(intersect_id, id_fieldname, table)
			dataset = 'umd-loss-gain'
		
			loss = gfw_api_request(geom, start_date, end_date, dataset, threshold=30)
			loss_field = 'loss_%s'% d
			print loss_field
			print loss
			update_table(table, loss_field, loss, intersect_id, id_fieldname)
			print orange
			orange+=1
 
def intersec_cal(table):
	
	i = 13
	while(i <= 13):
		c = str(2000 + i)
		d = str(2000 + i + 1)
		start_date = '%s-01-01' % c
		end_date = '%s-01-01' % d
		loss_in_geom(table, start_date, end_date, c)
		i+=1
 
 
def main():
	#summarize_loss_in_intersec('idn_adm2_protected','loss_2001_2013','historic_protected_areas_loss')
	#rate_loss_in_protected()
	#palm_concession_in_protected('idn_adm2_protected','idn_adm2_protected_palm_concession','area_hectare','concession_in_protected')
	#palm_concession_in_protected()
	#intersec_cal('district_illegal_concession')
	#palm_concession_in_protected('district_illegal_','district_illegal_concession','loss_2013','loss_concession_in_forest_estate')
	#palm_concession_in_protected('idn_adm2_risk_analysis','district_peat_','area_hectare','peat_land_area')
	#loss_in_geom('district_peat_union', '2001-01-01', '2014-01-01', '2001_2013')
	
	#palm_concession_in_protected('district_peat_','district_peat_union_concession','area_hectare','concession_on_peat')
 
main()
