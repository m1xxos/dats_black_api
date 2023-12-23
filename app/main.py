from app import dats_api, models

import time

import requests
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/scan")
async def scan():
    return await dats_api.scan()


@app.websocket("/scanWs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    tick = 0
    while True:
        data = await dats_api.scan()
        old_tick = tick
        tick = data['scan']['tick']
        if old_tick != tick:
            await websocket.send_json(data)
        time.sleep(1)


@app.post("/longScan")
async def long_scan(x: int, y: int):
    return await dats_api.long_scan(x, y)


@app.post("/shipCommand")
async def ship_command(ship_command_json: models.ShipCommand):
    return await dats_api.ship_command(ship_command_json.model_dump_json())


@app.get("/map")
async def get_map():
    area_map = await dats_api.get_map()
    print(area_map)
    island_map = requests.get(area_map['mapUrl']).json()
    islands_list = []
    for island in island_map['islands']:
        start_x = island['start'][0]
        start_y = island['start'][1]
        for y in island['map']:
            for x in y:
                if x == 1:
                    islands_list.append({'x': start_x, 'y': start_y})
                start_x += 1
            start_y += 1
            start_x = island['start'][0]
    area_map['island'] = islands_list
    return area_map
