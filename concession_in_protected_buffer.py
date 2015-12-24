import district_level_risk_analysis

"""Indicator: potential protected areas loss due to Gov't palm oil concessions """

def concession_in_protected_buffer_10km():
	"""step 1: create a 10km buffer around protected areas (“wdpa_idn_buffer_10km”):"""
	sql = """select st_buffer(the_geom_webmercator, 10km)
	  			from wdpa_idn"""

	"""step2: union to dissolve overlapping areas in “wdpa_idn_buffer_10km”, but in this way it dissolve all polygons into one big multipolygon. table name: wdpa_idn_buffer_10km_union"""

	sql = """SELECT st_union(the_geom) FROM wdpa_idn_buffer_10km"""

	"""step3: create table “idn_adm2_protected_buffer_10km”"""
	sql = """SELECT adm.id_2 adm_id, ST_Multi(ST_Buffer(ST_Intersection(protected.the_geom, adm.the_geom), 0.0)) as clipped_geom FROM 
		idn_adm2 adm
		LEFT JOIN wdpa_idn_buffer_10km_union protected
		ON ST_Intersects(adm.the_geom, protected.the_geom)
		WHERE Not ST_IsEmpty(ST_Buffer(ST_Intersection(adm.the_geom, protected.the_geom),0.0))"""

	"""step4: update area field:
	sql = """UPDATE idn_adm2_protected_buffer_10km
			set area_hectare = ST_Area(the_geom:: geography)/10000"""

	"""step5: Create table (idn_adm2_protected_buffer_10km_palm_concession_mof) from query. intersect idn_adm2_protected_buffer_10km with palm concession table."""
	sql = """SELECT adm_id, intersect_id, palm.objectid palm_id, ST_Multi(ST_Buffer(ST_Intersection(intersec.the_geom, palm.				the_geom), 0.0)) as clipped_geom FROM 
			idn_adm2_protected_buffer_10km_palm_concession_mof intersec 

			LEFT JOIN idn_oil_palm palm
			ON ST_Intersects(intersec.the_geom, palm.the_geom)
			WHERE Not ST_IsEmpty(ST_Buffer(ST_Intersection(intersec.the_geom, palm.the_geom),0.0))"""

	"""step6: update area field:"""
	sql = """update idn_adm2_protected_buffer_10km_palm_concession_mof
			set area_hectare = 
			st_area(the_geom::geography)/10000

	"""step7: call the function in 'district_level_risk_analysis.py'"""
	palm_concession_in_protected('idn_adm2_protected_buffer_10km','idn_adm2_protected_buffer_10km_palm_concession_mof','area_hectare','concession_in_protected_buffer_10km')


