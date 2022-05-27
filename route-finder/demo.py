import pickle5 as pickle

import datetime
from cv2 import mean
import coordinate
import pandas as pd
import numpy as np
from IPython.display import HTML

def calc_timedelta(str_time):
    delta = datetime.timedelta()
    for t in str_time.strip().split():
        if t.find('시간') != -1:
            delta += datetime.timedelta(hours=int(t.replace("시간", "")))
        elif t.find('분') != -1:
            delta += datetime.timedelta(minutes=int(t.replace("분", "")))
        elif t.find('초') != -1:
            delta += datetime.timedelta(seconds=int(t.replace("초", "")))
    return delta

def read_routes(org, des):
    filename = f'routes/{org}-{des}.pkl'

    org_coord = coordinate.get_coordinate(org)
    des_coord = coordinate.get_coordinate(des)
    (org_x, org_y) = coordinate.transform(org_coord[::-1], 'WGS84', 'WCONGNAMUL')
    (des_x, des_y) = coordinate.transform(des_coord[::-1], 'WGS84', 'WCONGNAMUL')

    with open(filename, 'rb') as f:
        data = pickle.load(f)

    org_routes, des_routes, bikes, bike_routes = data['org_routes'], data['des_routes'], data['bikes'], data['bike_routes']

    rows = []
    for i, srt in enumerate(bikes):
        (_, (srt_name, _, _, _, _, srt_coord)) = srt
        for j in range(i+1, len(bikes)):
            try:
                (_, (end_name, _, _, _, _, end_coord)) = bikes[j]
                route_id = f'{i}-{j}'

                try:    srt_calories = int(np.mean([float(route['info'].replace("kcal소모", "")) for route in org_routes[i]]))
                except: srt_calories = 0
                try:    end_calories = int(np.mean([float(route['info'].replace("kcal소모", "")) for route in des_routes[j]]))
                except: end_calories = 0
                try:    bike_calories = int(np.mean([float(route['calories'].replace("kcal", "")) for route in bike_routes[route_id]]))
                except: end_calories = 0
                total_calories = srt_calories + bike_calories + end_calories

                srt_time = calc_timedelta(min([route['time'] for route in org_routes[i]]))
                end_time = calc_timedelta(min([route['time'] for route in des_routes[j]]))
                bike_time = calc_timedelta(min([route['time'] for route in bike_routes[route_id]]))
                total_time = srt_time + bike_time + end_time

                srt_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={org_x},{org_y},{srt_coord[0]},{srt_coord[1]}&rt1={org}&rt2={srt_name}'
                end_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={end_coord[0]},{end_coord[1]},{des_x},{des_y}&rt1={end_name}&rt2={des}'
                bike_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=bike&rt={srt_coord[0]},{srt_coord[1]},{end_coord[0]},{end_coord[1]}&rt1={srt_name}&rt2={end_name}'
                total_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={org_x},{org_y},{des_x},{des_y}&rt1={org}&rt2={des}'

                rows.append([ \
                    route_id, \
                    f'<a href="{srt_link}">{org}</a>', \
                    str(srt_time), srt_calories, \
                    f'<a href="{bike_link}">{srt_name}</a>', \
                    str(bike_time), bike_calories, \
                    f'<a href="{end_link}">{end_name}</a>', \
                    str(end_time), end_calories, \
                    f'<a href="{total_link}">{des}</a>', \
                    str(total_time), total_calories, \
                ])
            except:
                pass

    df = pd.DataFrame(rows, columns="route_id org srt_time srt_calories srt_name bike_time bike_calories end_name end_time end_calories des total_time total_calories".split())
    df.set_index("route_id", inplace=True)
    return HTML(df.sort_values(by="total_time").to_html(escape=False))

if __name__ == "__main__":
    read_routes('낙성대공원', '몰로코')