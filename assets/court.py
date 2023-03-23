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
    midrange = polygons['three_point_line'].difference(paint)
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

def point_to_pass_region(point, court):
    point = shapely.Point(point[0], point[1])
    region = court[court.geometry.contains(point)]
    if region['name'].iloc[0] == 'in_the_paint':
        return 11
    if region['name'].iloc[0] == 'midrange':
        if point.y <= 14:
            return 5 if point.x <= 0 else 1
        else:
            if point.x <= -8:
                return 4
            elif point.x >= 8:
                return 2
            else:
                return 3
    if region['name'].iloc[0] == 'three_point_range':
        if point.y <= 14:
            return 7 if point.x <= 0 else 6
        else:
            if point.x <= -15:
                return 10
            elif point.x >= 15:
                return 8
            else:
                return 9
    return 11

if __name__ == '__main__':
    gdf, whole_court = initialize_court('./court.geojson')
    gdf[gdf['name'] == 'midrange'].geometry.plot()
    plt.xticks(list(range(-25, 25)))
    plt.show()
    print(gdf)
