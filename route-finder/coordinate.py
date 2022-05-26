import requests
import dotenv
from os import environ
from haversine import haversine

dotenv.load_dotenv('.env', override=True)
import pandas as pd

df_bus = pd.read_csv('data/bus.csv', encoding='euc-kr')
df_subway = pd.read_csv('data/subway.csv', encoding='euc-kr')
df_bike = pd.read_csv('data/bike.csv', encoding='cp949')

def transform(coord, input_coord='WCONGNAMUL', output_coord='WGS84'):
    URL = f'https://dapi.kakao.com/v2/local/geo/transcoord.json?x={coord[0]}&y={coord[1]}&input_coord={input_coord}&output_coord={output_coord}'
    headers = {'Authorization': f'KakaoAK {environ.get("KAKAO_REST_API_KEY")}'}
    new_coord = requests.get(URL, headers=headers).json()['documents'][0]
    return (new_coord['x'], new_coord['y'])

def get_distance(org, des):
    return haversine(org, des, unit='km')

def get_nearest_bike(lat, lng):
    delta = 5e-3
    df = df_bike[(df_bike["위도(Y)"] > lat-delta) & (df_bike["위도(Y)"] < lat+delta) \
               & (df_bike["경도(X)"] > lng-delta) & (df_bike["경도(X)"] < lng+delta) ]

    min_bike, min_dist = "N/A", float("inf")
    for i, bike in df.iterrows():
        dist = get_distance((lat, lng), bike[["위도(Y)", "경도(X)"]])
        if min_dist > dist:
            min_dist = dist
            min_bike = bike
    return min_dist, min_bike

def get_coordinate(keyword):
    URL = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={keyword}'
    headers = {'Authorization': f'KakaoAK {environ.get("KAKAO_REST_API_KEY")}'}
    coord = requests.get(URL, headers=headers).json()['documents'][0]
    return (float(coord['y']), float(coord['x']))
