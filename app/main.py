from app import dats_api, models
from app.nav import form_straight_line

import concurrent
import asyncio
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
    island_map = requests.get(area_map['mapUrl']).json()
    islands_list = []
    for island in island_map['islands']:
        start_x = island['start'][0]
        start_y = island['start'][1]
        maxWidth = 0
        currentIsland = {'x': start_x, 'y': start_y, 'height': len(island['map']), 'width': 0}
        for y in island['map']:
            if len(y) > maxWidth:
                maxWidth = len(y)
        currentIsland['width'] = maxWidth
        islands_list.append(currentIsland)
    area_map['island'] = islands_list
    return area_map


@app.get("/shipsUpdate")
async def update_ship():
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

      
@app.post('/navigate')
async def navigate(ship_id: int, x: int, y: int):
    await form_straight_line(ship_id, x, y)
    return 'Пошло-поехало'
      

@app.post("/addQueue")
async def add_queue(ship_command_json: models.ShipCommand):
    for ship in ship_command_json.ships:
        ships_commands[ship.id]['queue'].append(ship)
        ships_commands[ship.id]['size'] += 1


@app.get('/printQueue')
async def print_queue():
    print(ships_commands)
    return ships_commands

  
async def websocket_queue_endpoint():
    while True:
        data = {'ships': []}
        for ships_command in ships_commands:
            if int(ships_commands[ships_command]['size']) > 0:
                command = ships_commands[ships_command]['queue'].pop().model_dump()
                data['ships'].append(command)
                ships_commands[ships_command]['size'] -= 1
        print(data)
        print(await dats_api.ship_command(data))
        await asyncio.sleep(3)


@app.get('/startQueue')
async def start_queue():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, await websocket_queue_endpoint())


@app.get('/stopQueue')
async def stop_queue():
    loop = asyncio.get_event_loop()
    loop.close()
