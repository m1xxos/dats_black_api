from app import dats_api, models

import time

import requests
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

ship_ids = []
ships_commands = {}
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def get_ships_id():
    try:
        ships = await dats_api.scan()
        for ship in ships['scan']['myShips']:
            ship_ids.append(ship['id'])
        for ship_id in ship_ids:
            ships_commands[ship_id] = {}
            ships_commands[ship_id]['queue'] = []
            ships_commands[ship_id]['size'] = 0
    except:
        pass


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/scan")
async def scan():
    return await dats_api.scan()


@app.websocket("/scanWs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    json_data = await websocket.receive_json()



    tick = 0
    while True:
        data = await dats_api.scan()
        old_tick = tick
        tick = data['scan']['tick']
        if old_tick != tick:
            await websocket.send_json(data)

        time.sleep(1)


@app.websocket("/sendQueue")
async def websocket_queue_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = {'ships': []}
    while True:
        for ships_command in ships_commands:
            print(ships_commands[ships_command])
            if ships_commands[ships_command]['size'] > 0:
                command = ships_commands[ships_command]['queue'].pop().model_dump()
                data['ships'].append(command)
                ships_commands[ships_command]['size'] -= 1
        print(data)
        await websocket.send_json(await dats_api.ship_command(data))
        time.sleep(3)


@app.post("/longScan")
async def long_scan(x: int, y: int):
    return await dats_api.long_scan(x, y)


@app.post("/shipCommand")
async def ship_command(ship_command_json: models.ShipCommand):
    return await dats_api.ship_command(ship_command_json.model_dump_json())


@app.get("/map")
async def get_map():
    area_map = await dats_api.get_map()
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


@app.post("/addQueue")
async def add_queue(ship_command_json: models.ShipCommand):
    for ship in ship_command_json.ships:
        ships_commands[ship.id]['queue'].append(ship)
        ships_commands[ship.id]['size'] += 1


@app.get('/printQueue')
async def print_queue():
    print(ships_commands)
    return ships_commands
