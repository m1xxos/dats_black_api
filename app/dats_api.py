import requests


base_url = 'https://datsblack.datsteam.dev/api/'

base_headers = {'X-API-Key': 'aedd7d70-0f86-4869-99c9-325089da91b2'}


async def scan():
    method_addr = base_url + 'scan'
    r = requests.get(method_addr, headers=base_headers)
    return r.json()


async def long_scan(x, y):
    method_addr = base_url + 'longScan'
    json = {'x': x, 'y': y}
    r = requests.post(method_addr, headers=base_headers, json=json)
    return r.json()


async def ship_command(command_array):
    method_addr = base_url + 'shipCommand'
    r = requests.post(method_addr, headers=base_headers, json=command_array)
    return r.json()


async def get_map():
    method_addr = base_url + 'map'
    r = requests.get(method_addr, headers=base_headers)
    return r.json()
