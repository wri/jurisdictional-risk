import district_level_risk_analysis

def (peat_land_area):
	"""step 1: Create table (district_peat_) from query: intersect idn_adm2 with peat data:"""
	sql = """SELECT adm.id_2 adm_id, ST_Multi(ST_Buffer(ST_Intersection(peat.the_geom, adm.the_geom), 0.0))the_geom FROM 
			idn_adm2 adm 
			LEFT JOIN peat
			ON ST_Intersects(adm.the_geom, peat.the_geom)
			WHERE Not ST_IsEmpty(ST_Buffer(ST_Intersection(adm.the_geom, peat.the_geom),0.0))"""
	
	"""step 2: Add a “area_hectare” field, calculate area of each intersection by query:"""
	sql = """UPDATE district_peat_
			set area_hectare =          
			ST_Area(ST_Transform(the_geom,900913))/10000"""

	"""step 3: Calculate peat land area in district:"""
	palm_concession_in_protected('idn_adm2_risk_analysis','district_peat_','area_hectare','peat_land_area')

	"""step 4: Calculate loss on peat land from 2001 to 2013 in district:"""

	loss_in_geom('district_peat_union', '2001-01-01', '2014-01-01', '2001_2013')

	"""step 5: Create table (district_peat_union_concession) from query, calculate area"""



