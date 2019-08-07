import sys
import logging
import asyncio

from asyncua import ua, Server
from random import gauss
from random import seed
from datetime import datetime

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

seed(1)


def calc_temp(current_temp, count, modifier):
    temp = current_temp + gauss(0, 1)

    if count % modifier == 0:
        temp = current_temp + gauss(0, 1) + 20.0
    return temp


async def main():
    # setup our server
    server = Server()
    endpoint_url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
    if len(sys.argv) > 1:
        endpoint_url = sys.argv[1]
    print("Use Server Endpoint: " + endpoint_url)
    await server.init()
    server.set_endpoint(endpoint_url)
    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.codecentric.de'
    idx = await server.register_namespace(uri)
    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()
    # populating our address space
    _logger.info('Starting server!')

    band1 = await objects.add_object(idx, "Band1")
    pre_stage_temp = 25.0
    mid_stage_temp = 65.0
    post_stage_temp = 90.0
    pre_stage = await band1.add_variable(idx, "PreStage", pre_stage_temp)
    mid_stage = await band1.add_variable(idx, "MidStage", mid_stage_temp)
    post_stage = await band1.add_variable(idx, "PostStage", post_stage_temp)

    ts = await band1.add_variable(idx, "TimeStamp", datetime.now().isoformat())
    async with server:
        count = 0
        while True:
            await asyncio.sleep(0.5)
            count += 1
            now = datetime.now().isoformat()
            temp = calc_temp(pre_stage_temp, count, 200)
            temp2 = calc_temp(mid_stage_temp, count, 100)
            temp3 = calc_temp(post_stage_temp, count, 300)

            await pre_stage.set_value(temp)
            await mid_stage.set_value(temp2)
            await post_stage.set_value(temp3)
            await ts.set_value(now)
            _logger.info('Set value of %s to %.1f', temp, count)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    loop.run_until_complete(main())
    loop.close()
