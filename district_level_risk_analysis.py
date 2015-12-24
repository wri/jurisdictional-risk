import requests
import json
import simplejson
import numpy
import ee
from scipy import stats

ee.Initialize()

#APIURL = 'http://wri-01.cartodb.com/api/v2/sql'
#APIKEY = '0e5365cb1a299778e9df9c7bf6db489af8aa08e1'
GFW_APIURL = 'http://staging.gfw-apis.appspot.com/forest-change'

APIURL = 'http://wri-02.cartodb.com/api/v2/sql'
APIKEY = '437bccaeec274664457746f6299d929f4e35bbb9'




#protected area has fields that record tree cover loss in 2001-2013, sum of loss from 2001-2013, and fields that record the change rate from 2009-2013

def window(table):
	
	n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
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
			window_b = 'window_total_%s'% b
			print loss_a
			print loss_b
			print loss_c
			if loss_a is None:
				i+=1
				continue
			else:
				avg = (loss_a + loss_b + loss_c)/3
				print avg
				#update_table('idn_adm2_risk_analysis', window_b, avg,id_2, 'id_2')
				i+=1



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
			update_table('idn_adm2_risk_analysis', FieldInRiskTable, gradient,id_2, 'id_2')
			update_table('idn_adm2_risk_analysis', 'p_value_total_loss', p_value,id_2, 'id_2')
			update_table('idn_adm2_risk_analysis', 'r_squared_total_loss', r_value**2,id_2, 'id_2')


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

			"""Calculate tree cover loss in protected areas in 2001-2007"""

			intersect_loss_2001_list = get_intersect_values(intersec_table, 'loss_2001', 'adm_id', id_2)
			total_loss_2001 = sum_value(intersect_loss_2001_list)

			intersect_loss_2002_list = get_intersect_values(intersec_table, 'loss_2002', 'adm_id', id_2)
			total_loss_2002 = sum_value(intersect_loss_2002_list)

			intersect_loss_2003_list = get_intersect_values(intersec_table, 'loss_2003', 'adm_id', id_2)
			total_loss_2003 = sum_value(intersect_loss_2003_list)

			intersect_loss_2004_list = get_intersect_values(intersec_table, 'loss_2004', 'adm_id', id_2)
			total_loss_2004 = sum_value(intersect_loss_2004_list)

			intersect_loss_2005_list = get_intersect_values(intersec_table, 'loss_2005', 'adm_id', id_2)
			total_loss_2005 = sum_value(intersect_loss_2005_list)

			intersect_loss_2006_list = get_intersect_values(intersec_table, 'loss_2006', 'adm_id', id_2)
			total_loss_2006 = sum_value(intersect_loss_2006_list)

			intersect_loss_2007_list = get_intersect_values(intersec_table, 'loss_2007', 'adm_id', id_2)
			total_loss_2007 = sum_value(intersect_loss_2007_list)

			update_table('idn_adm2_risk_analysis', 'loss_2001', total_loss_2001, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2002', total_loss_2002, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2003', total_loss_2003, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2004', total_loss_2004, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2005', total_loss_2005, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2006', total_loss_2006, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2007', total_loss_2007, id_2,'id_2')

			"""Calculate tree cover loss in protected areas in 2008-2013"""

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

			update_table('idn_adm2_risk_analysis', 'loss_2008', total_loss_2008, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2009', total_loss_2009, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2010', total_loss_2010, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2011', total_loss_2011, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2012', total_loss_2012, id_2,'id_2')
			update_table('idn_adm2_risk_analysis', 'loss_2013', total_loss_2013, id_2,'id_2')
			"""

			try:

				change_rate09 = (total_loss_2009-total_loss_2008)/total_loss_2008
			
				change_rate10 = (total_loss_2010-total_loss_2009)/total_loss_2009
			
				change_rate11 = (total_loss_2011-total_loss_2010)/total_loss_2010
			
				change_rate12 = (total_loss_2012-total_loss_2011)/total_loss_2011
			
				change_rate13 = (total_loss_2013-total_loss_2012)/total_loss_2012

				avg_change_rate = numpy.mean([change_rate09, change_rate10, change_rate11, change_rate12, change_rate13])
				update_table('idn_adm2_risk_analysis', 'rate_of_loss_in_protected_areas', avg_change_rate, id_2,'id_2')

			except ZeroDivisionError:
				continue"""

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
	#id_fieldname = 'intersect_id'
	id_fieldname = 'adm_id'
	
	ids = get_all_ids(table, id_fieldname)
	print ids
	orange = 0
	for intersection in ids:
		
		#intersect_id = intersection['intersect_id']
		intersect_id = intersection['adm_id']
		print intersect_id
		#if intersect_id == 504:
		geom = get_geoms(intersect_id, id_fieldname, table)
		#geom = get_simple_geoms(intersect_id, id_fieldname, table)
		dataset = 'umd-loss-gain'
		
		loss = gfw_api_request(geom, start_date, end_date, dataset, threshold=30)
		#loss_field = 'loss_%s'% d
		loss_field = 'total_loss_%s'% d
		print loss_field
		print loss
		update_table(table, loss_field, loss, intersect_id, id_fieldname)
		print orange
		orange+=1

def loss_ee_area(areaimg, theid,table, id_fieldname):
	query = """
        SELECT the_geom
        FROM %s
        WHERE %s = '%s'""" % (table,id_fieldname, theid)
	r = requests.get(APIURL, params=dict(api_key=APIKEY, q=query, format='geojson'))
	try:
		geoms = r.json()['features'][0]['geometry']['coordinates']
	#except TypeError:
		# no geoms
		#return None
	except IndexError:
		return None
	geoms_sss = geoms[0][0]
	feature = ee.Geometry.Polygon(geoms_sss)
	#stats = areaimg.reduceRegion({'reducer': ee.Reducer.sum(),'geometry':feature,'maxPixels': 5e9})
	stats = areaimg.reduceRegion(ee.Reducer.sum(), feature)

	try:
		area = stats.getInfo()['b1']
		#area = stats.getInfo()['lossyear']
		area_ha = area/ 10000
		print area_ha
		return area_ha
	except ee.ee_exception.EEException:
		#The region has too many pixels;
		return 99999

def raster_with_umd(rasterImg,year_s, year_e):
	
	umd = ee.Image('UMD/hansen/global_forest_change_2014')
	treeCover = umd.select(['treecover2000'])
	"""Create an image where pixels >=30 get the value 1 and all other pixels get the // value 0"""
	treeExtent = treeCover.gte(30)
	year = umd.select(['lossyear'])
	"""Create an image where pixels between year_s and year_e get the value 1 and all other pixels get the // value 0"""
	umdloss = year.gte(year_s).And(year.lte(year_e))
	umdlossExtent = umdloss.And(treeExtent)
	
	loss_Img = rasterImg.And(umdlossExtent)
	areaimg = loss_Img.multiply(ee.Image.pixelArea())
	return areaimg

def get_raster_area(raster, loss):
	if raster == 'carbon':
		image = ee.Image('GME/images/06900458292272798243-10265563443515643977')
		"""Create an image where pixels of medium and high carbon stock get the value 1 and all other pixels get the value 0"""
		"""HCS area of 40 Mg C/Ha"""
		image_rcl = image.gte(40)

	elif raster == 'primary':
		image = ee.Image('GME/images/06900458292272798243-17233255607601779355')
		"""Create an image where pixels of primary forest as of year 2000 get the value 1 and all other pixels get the value 0"""
		image_rcl = image.neq(3)  #not equal to 3, 3 is the only value to exclude here

	if loss== True:
		areaImg = raster_with_umd(image_rcl, 1, 13)

	elif loss== False:
		areaImg = image_rcl.multiply(ee.Image.pixelArea())



	return areaImg

def loss_on_raster_in_district(table,dataset,loss,fieldname):
	
	areaimg = get_raster_area(dataset, loss)
	
	n = 441 #441 districts in Indonedsia, id_2 values ranging from 1 to 441
	for id_2 in range(1,n+1):
		print id_2
		area = loss_ee_area(areaimg,id_2,table,fieldname)
		if loss == False:
			field = '%s_area' % dataset
		elif loss == True:
			field = 'loss_on_%s' % dataset
		update_table(table, field, area,id_2, fieldname)
		
def loss_on_raster_in_intersections(table,dataset,loss):
	areaimg = get_raster_area(dataset, loss)
	id_fieldname = 'intersect_id'
	ids = get_all_ids(table, id_fieldname)
	for intersection in ids:
		intersect_id = intersection['intersect_id']
		print intersect_id
		area = loss_ee_area(areaimg,intersect_id,table,id_fieldname)
		field = '%s_area' % dataset
		update_table(table, field, area,intersect_id, id_fieldname)

def intersec_cal(table):
	
	i = 1
	while(i <= 12):
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
	
	#loss_on_raster_in_district('idn_adm2_risk_analysis', 'primary', False, 'id_2')
	#loss_on_raster_in_district('idn_adm2_risk_analysis', 'carbon', False, 'id_2')
	#loss_on_raster_in_district('idn_adm2_risk_analysis','carbon', True, 'id_2')
	#loss_on_raster_in_district('idn_adm2_risk_analysis','primary', True, 'id_2')
	#loss_on_raster_in_district('idn_adm2_palm','primary', False, 'adm_id')
	#loss_on_raster_in_district('idn_adm2_concession_mof','carbon', False, 'adm_id')
	#loss_on_raster_in_intersections('idn_adm2_concession_mof_intersec_','carbon', False)



	#intersec_cal('district_illegal_concession_mof')
	#palm_concession_in_protected('district_illegal_','district_illegal_concession_mof','loss_2013','loss_concession_in_forest_estate')
	#palm_concession_in_protected('idn_adm2_protected','idn_adm2_protected_palm_concession_mof','area_hectare','concession_in_protected')
	#palm_concession_in_protected('idn_adm2_protected_buffer_10km','idn_adm2_protected_buffer_10km_palm_concession_mof','area_hectare','concession_in_protected_buffer_10km')

	#intersec_cal('idn_adm2_protected')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2001', 'loss_2001')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2005', 'loss_2005')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2006', 'loss_2006')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2006', 'loss_2006')
	#window('idn_adm2_risk_analysis')
	#summarize_loss_in_intersec('idn_adm2_protected', 'loss_2001', 'loss_2001')
	#regression('idn_adm2_risk_analysis', 'adm_id')

	
	#intersec_cal('district_peat_union')
	#intersec_cal('idn_adm2_risk_analysis')
	#regression_window('idn_adm2_risk_analysis')
	#regression_window('district_peat_union')
	regression_window('idn_prim_loss_0012_district_local')



main()


