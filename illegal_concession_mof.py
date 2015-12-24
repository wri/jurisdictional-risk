import district_level_risk_analysis

"""Indicator: potential protected areas loss due to Gov't palm oil concessions """

def (district_illegal_concession_mof):

	"""step 1: Create table (district_illegal_) from query: intersect idn_adm2 with legal data where there is forest estate:"""

	"""step 2: Add a “area_hectare” field, calculate area of each intersection by query:

	sql = """
			update district_illegal_
			set area_hectare =
			st_area(the_geom::geography)/10000"""

	sql = """
			WITH illegal AS (SELECT * FROM indonesia_legal_2
			WHERE kh_fungsi_='HP' OR kh_fungsi_='HPT')
			SELECT adm.id_2 adm_id, 
			ST_Multi(ST_Buffer(ST_Intersection(illegal.the_geom, adm.the_geom), 0.0))
			as clipped_geom FROM idn_adm2 adm 
			LEFT JOIN illegal
			ON ST_Intersects(adm.the_geom, illegal.the_geom)
			WHERE Not ST_IsEmpty(ST_Buffer(ST_Intersection(adm.the_geom, illegal.the_geom),0.0))"""

	"""step 3: Create table (district_illegal_concession_mof) from query:"""
	sql = """
			SELECT adm_id,palm.objectid palm_id, 
			ST_Multi(ST_Buffer(ST_Intersection(intersec.the_geom, palm.the_geom), 0.0))the_geom FROM 
			district_illegal_ intersec 
			LEFT JOIN idn_oil_palm palm
			ON ST_Intersects(intersec.the_geom, palm.the_geom)
			WHERE Not ST_IsEmpty(ST_Buffer(ST_Intersection(intersec.the_geom, palm.the_geom),0.0))
			"""

	"""step 4: Add a field “loss_2013” in table “district_illegal_concession"""

	"""step 5: call function"""
	sql = """intersec_cal('district_illegal_concession_mof')
	palm_concession_in_protected('district_illegal_','district_illegal_concession_mof','loss_2013','loss_concession_in_forest_estate')