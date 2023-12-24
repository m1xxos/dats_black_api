import app.dats_api as dats_api
import asyncio
async def form_straight_line(id: int, end_x: int, end_y: int):
    sheesh = await dats_api.scan()
    ship_stat = next(item for item in sheesh['scan']['myShips'] if item['id'] == id)
    if ship_stat['x'] != end_x and ship_stat['y'] != end_y:
        return []
    if ship_stat['x'] > end_x:
        distance = ship_stat['x'] - end_x
        if ship_stat['direction'] == 'north':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': -90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'south':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'west':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
    elif ship_stat['x'] < end_x:
        distance = end_x - ship_stat['x']
        if ship_stat['direction'] == 'north':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'south':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': -90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'east':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
    elif ship_stat['y'] > end_y:
        distance = ship_stat['y'] - end_y
        if ship_stat['direction'] == 'west':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': -90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'east':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'south':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
    elif ship_stat['y'] < end_y:
        distance = end_y - ship_stat['y']
        if ship_stat['direction'] == 'west':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'east':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': -90}]})
            await asyncio.sleep(3)
        if ship_stat['direction'] == 'north':
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
            await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'rotate': 90}]})
            await asyncio.sleep(3)
    else:
        distance = 0
    print(distance)
    await calculate_speed(distance, ship_stat)



async def calculate_speed(distance: int, ship_stat: dict):
    current_speed = ship_stat['speed']
    while distance > 0:
        brake_length = 0
        speed = current_speed
        print(current_speed)
        while speed > 0:
            brake_length += speed
            speed -= ship_stat['maxChangeSpeed']
        if brake_length >= distance:
            if current_speed <= ship_stat['maxChangeSpeed']:
                await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'changeSpeed': -current_speed}]})
                await asyncio.sleep(3)
                current_speed = 0
            else:
                await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'changeSpeed': -ship_stat['maxChangeSpeed']}]})
                await asyncio.sleep(3)
                current_speed -= ship_stat['maxChangeSpeed']
        else:
            if current_speed + ship_stat['maxChangeSpeed'] <= ship_stat['maxSpeed']:
                await dats_api.ship_command({'ships':
                    [{'id': ship_stat['id'], 'changeSpeed': ship_stat['maxChangeSpeed']}]})
                await asyncio.sleep(3)
                current_speed += ship_stat['maxChangeSpeed']
            else:
                await dats_api.ship_command({'ships':
                    [{'id': ship_stat['id'], 'changeSpeed': ship_stat['maxSpeed']-current_speed}]})
                await asyncio.sleep(3)
                current_speed = ship_stat['maxSpeed']
        distance = distance - current_speed
    else:
        await dats_api.ship_command({'ships': [{'id': ship_stat['id'], 'changeSpeed': -current_speed}]})
