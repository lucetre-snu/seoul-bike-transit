import pickle5 as pickle

import datetime
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


def calc_distdelta(str_dist):
    delta = 0
    for d in str_dist.strip().split():
        if d.find('km') != -1:
            delta += float(d.replace("km", "")) * 1000
        elif d.find('m') != -1:
            delta += float(d.replace("m", ""))
    return delta


def get_calo(srt_routes, end_routes, bike_routes):
    try:
        srt_calo = int(np.mean(
            [float(route['info'].replace("kcal소모", "")) for route in srt_routes]))
    except:
        srt_calo = 0
    try:
        end_calo = int(np.mean(
            [float(route['info'].replace("kcal소모", "")) for route in end_routes]))
    except:
        end_calo = 0
    try:
        bike_calo = int(np.mean([float(route['calories'].replace(
            "kcal", "")) for route in bike_routes]))
    except:
        bike_calo = 0
    total_calo = srt_calo + bike_calo + end_calo
    return (total_calo, srt_calo, end_calo, bike_calo)


def get_time(srt_routes, end_routes, bike_routes):
    srt_time = calc_timedelta(
        min([route['time'] for route in srt_routes]))
    end_time = calc_timedelta(
        min([route['time'] for route in end_routes]))
    bike_time = calc_timedelta(
        min([route['time'] for route in bike_routes]))
    total_time = srt_time + bike_time + end_time
    return (total_time, srt_time, end_time, bike_time)


def get_dist(srt_routes, end_routes, bike_routes):
    srt_dist = min([calc_distdelta(route['info']) for route in srt_routes])
    end_dist = min([calc_distdelta(route['info']) for route in end_routes])
    bike_dist = min([calc_distdelta(route['distance'])
                    for route in bike_routes])
    total_dist = srt_dist + bike_dist + end_dist
    return (total_dist/1000, srt_dist/1000, end_dist/1000, bike_dist/1000)


def read_routes(org, des):
    filename = f'routes/{org}-{des}.pkl'

    org_coord = coordinate.get_coordinate(org)
    des_coord = coordinate.get_coordinate(des)
    (org_x, org_y) = coordinate.transform(
        org_coord[::-1], 'WGS84', 'WCONGNAMUL')
    (des_x, des_y) = coordinate.transform(
        des_coord[::-1], 'WGS84', 'WCONGNAMUL')

    with open(filename, 'rb') as f:
        data = pickle.load(f)

    org_routes, des_routes, bikes, bike_routes = data['org_routes'], data[
        'des_routes'], data['bikes'], data['bike_routes']

    rows = []
    for i, srt in enumerate(bikes):
        (_, (srt_name, _, _, _, _, srt_coord)) = srt
        for j in range(i+1, len(bikes)):
            try:
                (_, (end_name, _, _, _, _, end_coord)) = bikes[j]
                route_id = f'{i}-{j}'

                # print('org_routes', org_routes[i])
                # print('des_routes', des_routes[j])
                # print('bike_routes', bike_routes[route_id])

                (total_calo, srt_calo, end_calo, bike_calo) = get_calo(
                    org_routes[i], des_routes[j], bike_routes[route_id])
                (total_time, srt_time, end_time, bike_time) = get_time(
                    org_routes[i], des_routes[j], bike_routes[route_id])
                (total_dist, srt_dist, end_dist, bike_dist) = get_dist(
                    org_routes[i], des_routes[j], bike_routes[route_id])

                # print((total_dist, srt_dist, end_dist, bike_dist))

                srt_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={org_x},{org_y},{srt_coord[0]},{srt_coord[1]}&rt1={org}&rt2={srt_name}'
                end_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={end_coord[0]},{end_coord[1]},{des_x},{des_y}&rt1={end_name}&rt2={des}'
                bike_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=bike&rt={srt_coord[0]},{srt_coord[1]},{end_coord[0]},{end_coord[1]}&rt1={srt_name}&rt2={end_name}'
                total_link = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={org_x},{org_y},{des_x},{des_y}&rt1={org}&rt2={des}'

                rows.append([
                    route_id,
                    f'<a href="{srt_link}">{org}</a>',
                    str(srt_time), srt_calo, srt_dist,
                    f'<a href="{bike_link}">{srt_name}</a>',
                    str(bike_time), bike_calo, bike_dist,
                    f'<a href="{end_link}">{end_name}</a>',
                    str(end_time), end_calo, end_dist,
                    f'<a href="{total_link}">{des}</a>',
                    str(total_time), total_calo, total_dist,
                ])
            except Exception as e:
                print(e)
                pass

    df = pd.DataFrame(
        rows, columns="route_id org srt_time srt_calo srt_dist srt_name bike_time bike_calo bike_dist end_name end_time end_calo end_dist des total_time total_calo total_dist".split())
    df.set_index("route_id", inplace=True)
    return HTML(df.sort_values(by="total_time").to_html(escape=False))


if __name__ == "__main__":
    read_routes('낙성대공원', '몰로코')
