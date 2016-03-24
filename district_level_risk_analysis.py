import requests
import json
import simplejson
import numpy
import ee
from scipy import stats

"""CartoDB API authentication and GFW url endpoint"""
GFW_APIURL = 'http://staging.gfw-apis.appspot.com/forest-change'

APIURL = 'http://wri-02.cartodb.com/api/v2/sql'
APIKEY = '437bccaeec274664457746f6299d929f4e35bbb9'




#protected area has fields that record tree cover loss in 2001-2013, sum of loss from 2001-2013, and fields that record the change rate from 2009-2013

def window(table): #applies the moving window method to the table.
	
	n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
	for id_2 in range(1, n+1):
		print id_2
		i = 2
		while(i <= 12):#average loss from year 2002(avg of 2001,2002,2003) to 2012(avg of 2011,2012,2013)
			b = str(2000 + i)
			a = str(2000 + i - 1)
			c = str(2000 + i + 1)
			#fb = 'loss_%s'% b
			fb = 'total_loss_%s'% b
			#fa = 'loss_%s'% a
			fa = 'total_loss_%s'% a
			#fc = 'loss_%s'% c
			fc = 'total_loss_%s'% c
			#For a specific year, get the loss of that year, as well as the loss of before and after years.
			loss_a = get_intersect_values(table,fa,'adm_id', id_2)[0][fa]
			loss_b = get_intersect_values(table,fb,'adm_id', id_2)[0][fb]
			loss_c = get_intersect_values(table,fc,'adm_id', id_2)[0][fc]
			window_b = 'window_total_%s'% b #
			print loss_a
			print loss_b
			print loss_c
			if loss_a is None:
				i+=1
				continue
			else:
				avg = (loss_a + loss_b + loss_c)/3 #Calculate the average.
				print avg
				update_table('idn_adm2_risk_analysis', window_b, avg,id_2, 'id_2') #Update the table.
				i+=1


# For each of the 441 districts, this function 1)firstly applies the moving window method to the tree cover loss, 
# and 2) then fits a linear regression line to the moving-window-applied loss, and updates the table with the slope, r-squared, and p-value.
def regression(table, id_fieldname):
	n = 441
	for id_2 in range(1, n+1):
		print id_2

		i = 2
		while(i <= 12):
			b = str(2000 + i)
			a = str(2000 + i - 1)
			c = str(2000 + i + 1)
			#fb = 'loss_%s'% b
			fb = 'total_loss_%s'% b
			#fa = 'loss_%s'% a
			fa = 'total_loss_%s'% a
			#fc = 'loss_%s'% c
			fc = 'total_loss_%s'% c
			loss_a = get_intersect_values(table,fa,'adm_id', id_2)[0][fa]
			loss_b = get_intersect_values(table,fb,'adm_id', id_2)[0][fb]
			loss_c = get_intersect_values(table,fc,'adm_id', id_2)[0][fc]
			window_b = 'window_%s'% b
			if loss_a is None:
				i+=1
				continue
			else:
				window_b = (loss_a + loss_b + loss_c)/3
					
		y = [window_2002,window_2003,window_2004,
				window_2005,window_2006,window_2007,
				window_2008,window_2009,window_2010,
				window_2011,window_2012]
		
		x = [2,3,4,5,6,7,8,9,10,11,12]
		if window_2002 is None:
			continue
		else:
			gradient, intercept, r_value, p_value, std_err = stats.linregress(x,y)
			print "Gradient, ntercept, R-squared, std_err", gradient, intercept, r_value**2, std_err
			FieldInRiskTable = 'rate_total_loss'
			update_table('idn_adm2_risk_analysis', FieldInRiskTable, gradient,id_2, 'id_2') #Update the table with the slope of the fitting line
			update_table('idn_adm2_risk_analysis', 'p_value_total_loss', p_value,id_2, 'id_2') #Update the table with the p-value of the coefficient
			update_table('idn_adm2_risk_analysis', 'r_squared_total_loss', r_value**2,id_2, 'id_2')#Update the table with the r-square of the regression

#This function does the same thing with the function above, just tweaked to fit specific fields of the table.
def regression_window(table):
	
	#n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
	#for id_2 in range(1, n+1):
	n = 441
	for cartodb_id in range(1, n+1):
		#print id_2
		print cartodb_id
		y = []
		i = 2
		while(i <= 12):
			b = str(2000 + i)
			a = str(2000 + i - 1)
			c = str(2000 + i + 1)
			#fb = 'loss_%s'% b
			fb = 'loss_%s'% b
			#fa = 'loss_%s'% a
			fa = 'loss_%s'% a
			#fc = 'loss_%s'% c
			fc = 'loss_%s'% c
			#loss_a = get_intersect_values(table,fa,'adm_id', id_2)[0][fa]
			#loss_b = get_intersect_values(table,fb,'adm_id', id_2)[0][fb]
			#loss_c = get_intersect_values(table,fc,'adm_id', id_2)[0][fc]
			loss_a = get_intersect_values(table,fa,'cartodb_id', cartodb_id)[0][fa]
			loss_b = get_intersect_values(table,fb,'cartodb_id', cartodb_id)[0][fb]
			loss_c = get_intersect_values(table,fc,'cartodb_id', cartodb_id)[0][fc]
			print loss_a
			print loss_b
			print loss_c
			if loss_a is None:
				i+=1
				continue
			else:
				avg = (loss_a + loss_b + loss_c)/3
				y.append(avg)
				i+=1
		if y== []:
			continue
		else:
			print y
			x = [2,3,4,5,6,7,8,9,10,11,12]
		
			gradient, intercept, r_value, p_value, std_err = stats.linregress(x,y)
			print "Gradient, ntercept, R-squared, std_err", gradient, intercept, r_value**2, std_err
			FieldInRiskTable = 'rate_primary_loss'
			#update_table('idn_adm2_risk_analysis', FieldInRiskTable, gradient,id_2, 'id_2')
			#update_table('idn_adm2_risk_analysis', 'p_value_peat_loss', p_value,id_2, 'id_2')
			#update_table('idn_adm2_risk_analysis', 'r_squared_peat_loss', r_value**2,id_2, 'id_2')

			update_table(table, FieldInRiskTable, gradient,cartodb_id, 'cartodb_id')
			update_table(table, 'p_value_primary_loss', p_value,cartodb_id, 'cartodb_id')
			update_table(table, 'r_squared_primary_loss', r_value**2,cartodb_id, 'cartodb_id')

# For each of the 441 districts, calculate the percentage area of the intersection with a layer(intersected area with protected/primary/ over the entire area of district)
def summarize_loss_in_intersec(intersec_table, FieldOfInterest, FieldInRiskTable):
	n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
	for id_2 in range(1, n+1):
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

#Intersec_table is the intersection layer of district table and protected/primary forest, overlapping_table is the intersection layer of district table, protected/primary forest, and palm oil concessions
#This function calculates the porprotion of concession area over protected/primary forest, per district
def palm_concession_in_protected(intersec_table,overlapping_table,FieldOfInterest,FieldInRiskTable):
	
	n = 441
	for id_2 in range(1,n+1):
		print id_2
		intersect_area_list = get_intersect_values(intersec_table,'area_hectare','adm_id', id_2)
		if len(intersect_area_list)==0:
			continue
		else:
			total_intersec_area = sum_value(intersect_area_list)
			print total_intersec_area
			print overlapping_table
			print FieldOfInterest
			print id_2
			overlapping_area_list = get_intersect_values(overlapping_table,FieldOfInterest,'adm_id', id_2)
			
			try:
				total_overlapping_area = sum_value(overlapping_area_list)
				perc = total_overlapping_area/total_intersec_area
				update_table('idn_adm2_risk_analysis', FieldInRiskTable, perc, id_2,'id_2')


			except ZeroDivisionError:
					continue

def update_table(table, field, value, identifier, id_fieldname):

	if value is None:
		value = 0
	query = """
			UPDATE %s SET %s = %f
			WHERE %s = %d""" % (table,field, value, id_fieldname, identifier)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
	

#This function gets the list of values of a field for a specific where_value from CartoDB
def get_intersect_values(table, fieldname, where_name, where_value):	
	query = """
			SELECT %s FROM %s where %s = %s""" % (fieldname, table, where_name, where_value)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
	value_list = r.json()['rows']
	return value_list

#This function gets the list of ids from the table on CartoDB
def get_all_ids(table, id_fieldname):	
	query = """
			SELECT %s FROM %s""" % (id_fieldname, table)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query))
	id_list = r.json()['rows']
	return id_list
	
#This function gets the geometry of a polygon
def get_geoms(intersect_id, id_fieldname, table):
    query = """
            SELECT the_geom FROM %s
    		WHERE %s = '%s'""" % (table, id_fieldname, intersect_id)

    r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query, format='geojson'))

    geoms = r.json()['features'][0]['geometry']
    strgeom = json.dumps(geoms)
    return strgeom
    
#This function gets the simple geometry of a polygon. This is used only when the get_geoms function causes error due to the complexity of the polygon
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

#Adding up the areas
def sum_value(valuelist):
	total_value = 0
	for next_value in valuelist:
		value = next_value.values()[0]
		total_value += value
	return total_value

#Using GFW API to calculate tree cover loss/forma alerts. Documentations on https://github.com/wri/gfw-api
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

def main():
	#summarize_loss_in_intersec('idn_adm2_protected','loss_2001_2013','historic_protected_areas_loss')
	#palm_concession_in_protected('idn_adm2_protected','idn_adm2_protected_palm_concession','area_hectare','concession_in_protected')
	#palm_concession_in_protected()
	#palm_concession_in_protected('district_illegal_','district_illegal_concession','loss_2013','loss_concession_in_forest_estate')
	#palm_concession_in_protected('idn_adm2_risk_analysis','district_peat_','area_hectare','peat_land_area')
	
	#palm_concession_in_protected('district_peat_','district_peat_union_concession','area_hectare','concession_on_peat')
	#intersec_cal('district_illegal_concession_mof')
	#palm_concession_in_protected('district_illegal_','district_illegal_concession_mof','loss_2013','loss_concession_in_forest_estate')
	#palm_concession_in_protected('idn_adm2_protected','idn_adm2_protected_palm_concession_mof','area_hectare','concession_in_protected')
	#palm_concession_in_protected('idn_adm2_protected_buffer_10km','idn_adm2_protected_buffer_10km_palm_concession_mof','area_hectare','concession_in_protected_buffer_10km')

	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2001', 'loss_2001')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2005', 'loss_2005')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2006', 'loss_2006')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2006', 'loss_2006')
	#window('idn_adm2_risk_analysis')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2001', 'loss_2001')
	#regression('idn_adm2_risk_analysis', 'adm_id')

	
	#regression_window('idn_adm2_risk_analysis')
	#regression_window('district_peat_union')
	regression_window('idn_prim_loss_0012_district_local')



main()


