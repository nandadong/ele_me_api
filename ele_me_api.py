#!/usr/bin/env python
import os
import sys
import json
import time
import pprint
import logging
import getpass
import argparse


import s2sphere
from s2sphere import CellId, math

import requests


def break_down_area_to_cell(north, south, west, east):
    """ Return a list of s2 cell id """
    result = []

    region = s2sphere.RegionCoverer()
    region.min_level = 15
    region.max_level = 15
    p1 = s2sphere.LatLng.from_degrees(north, west)
    p2 = s2sphere.LatLng.from_degrees(south, east)
    cell_ids = region.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
    result += [ cell_id.id() for cell_id in cell_ids ] 

    return result

def get_position_from_cell_id(cellid):
    cell = CellId(id_ = cellid).to_lat_lng()
    return (math.degrees(cell._LatLng__coords[0]), math.degrees(cell._LatLng__coords[1]), 0)

def search_point(cell_id):
    position = get_position_from_cell_id(cell_id) 
    latitude = position[0]
    longitude = position[1]
    limit = 5
    order_by = 6
    payload = {'latitude': latitude, 'longitude': longitude, 'limit': limit, 'order_by': order_by}
    url = "https://mainsite-restapi.ele.me/shopping/restaurants/"
    response_dict = requests.get(url, params=payload).content
    return response_dict

def parse_restaurant(search_response):
    restaurant_info = json.loads(search_response)[0]
    restaurant = restaurant_info["name"]
    
    return restaurant	

def scan_area(north, south, west, east):
    result = []

    cell_ids = break_down_area_to_cell(north, south, west, east)
    count = 0            
    for cell_id in cell_ids:
        search_response = search_point(cell_id)

        # Parse restaurant info
        if search_response is None:
        	continue
        restaurant = parse_restaurant(search_response)
        # Aggregate restaurant info and return
        result.append(restaurant)

    return result
    
if __name__ == "__main__":
    north = 39.9366975
    south = 39.9038591
    west = 116.3538877
    east = 116.435177
    myjson = scan_area(north, south, west, east)
    print json.dumps(myjson, indent=2, ensure_ascii=False)
    