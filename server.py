import asyncio
import json
import logging
import websockets
import socket
import names
import os
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from multiprocessing import Pipe, Process, current_process


logging.basicConfig(level=logging.INFO)


def echo_server(pipe: Pipe):
    name = current_process().name
    logging.debug(f'{name} started...')

    sock = socket.socket()
    sock.bind(('', 9090))
    sock.listen(1)
    conn, addr = sock.accept()

    res = bytes()

    while True:
        data = conn.recv(1024)
        if not data:
            break
        res += data

    pipe.send(res)

    conn.close()
    logging.debug(f'{name} stopped...')
    return res


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def send_to_clients_list(self, message: list):
        if self.clients:
            message_b = json.dumps(message).encode('utf-8')
            print('message_b', message_b)
            [await client.send(message_b) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if not message:
                pass

            elif message.split()[0] == "exchange":

                recipient, sender = Pipe()

                thread = Process(target=echo_server, args=(sender, ))
                thread.start()

                os.system(f"python main.py {message} {ws.name}")

                byte_res = recipient.recv()
                res = json.loads(byte_res)

                await self.send_to_clients_list([ws.name, res])

            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())
