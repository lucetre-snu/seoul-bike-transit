import pickle
import navigator
import coordinate
import pandas as pd
from IPython.display import HTML

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
        (_, (srt_name, srt_lat, srt_lng, _, _, srt_coord)) = srt
        for j in range(i+1, len(bikes)):
            try:
                (_, (end_name, end_lat, end_lng, _, _, end_coord)) = bikes[j]
                route_id = f'{i}-{j}'
                srt_time = navigator.calc_timedelta(min([route['time'] for route in org_routes[i]]))
                bike_time = navigator.calc_timedelta(min([route['time'] for route in bike_routes[route_id]]))
                end_time = navigator.calc_timedelta(min([route['time'] for route in des_routes[j]]))
                total_time = srt_time + bike_time + end_time

                link1 = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={org_x},{org_y},{srt_coord[0]},{srt_coord[1]}&rt1={org}&rt2={srt_name}'
                link2 = f'https://map.kakao.com/?map_type=TYPE_MAP&target=bike&rt={srt_coord[0]},{srt_coord[1]},{end_coord[0]},{end_coord[1]}&rt1={srt_name}&rt2={end_name}'
                link3 = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={end_coord[0]},{end_coord[1]},{des_x},{des_y}&rt1={end_name}&rt2={des}'
                link4 = f'https://map.kakao.com/?map_type=TYPE_MAP&target=transit&rt={org_x},{org_y},{des_x},{des_y}&rt1={org}&rt2={des}'

                rows.append([ \
                    route_id, \
                    org, \
                    f'<a href="{link1}">{srt_time}</a>', \
                    srt_name, \
                    f'<a href="{link2}">{bike_time}</a>', \
                    end_name, \
                    f'<a href="{link3}">{end_time}</a>', \
                    des, \
                    f'<a href="{link4}">{total_time}</a>', \
                ])
            except:
                pass

    df = pd.DataFrame(rows, columns=["route_id", "org", "srt_time", "srt_name", "bike_time", "end_name", "end_time", "des", "total_time"])
    df.set_index("route_id", inplace=True)
    return HTML(df.sort_values(by="total_time").to_html(escape=False))