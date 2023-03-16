import shapely
import json
import matplotlib.pyplot as plt
import geopandas as gpd
import os
from .assets import DistanceBucket

def initialize_court(path):
    court = json.load(open(path, 'r'))
    polygons = {}

    for i in court["geoJSON"]["features"]:
        ls = shapely.LineString(i['geometry']['coordinates'][0])
        poly = ls.convex_hull
        polygons[i['properties']['name']] = poly

    paint = polygons['outer_key']
    midrange = polygons['three_point_line']
    restricted_area = polygons['restricted']
    three_point_range = polygons['perimeter'].difference([polygons['three_point_line']])
    whole_court = polygons['perimeter']
    poly_list = {
        'name': ['restricted_area', 'in_the_paint', 'midrange', 'three_point_range'],
        'geometry': [restricted_area, paint, midrange, three_point_range[0]]
    }
    gdf = gpd.GeoDataFrame(poly_list).set_geometry('geometry')
    return gdf, whole_court

def point_to_region(point, court):
    point = shapely.Point(point[0], point[1])
    region_name = court[court.geometry.contains(point)]['name'].iloc[0].upper()
    return DistanceBucket[region_name]



if __name__ == '__main__':
    gdf, whole_court = initialize_court('./court.geojson')
    print(gdf)
