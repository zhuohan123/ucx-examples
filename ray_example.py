import asyncio
import time
import ucp
import torch
import numpy as np
import ray

n_elements = 2**10
host = "127.0.0.1"
port = 13337

@ray.remote(num_gpus=1)
class Server:
    def __init__(self):
        # Initialize PyTorch
        _ = torch.rand(1, dtype=torch.float, device='cuda')
    async def run_concurrent(self):
        self.my_data = torch.rand(n_elements, dtype=torch.float, device='cuda')
        print("server data:", self.my_data)
        # Start server listener
        self.lf = ucp.create_listener(self.call_back, port)
        while not self.lf.closed():
            await asyncio.sleep(0.1)

    async def call_back(self, ep):
        print("Sending data to client")
        await ep.send(self.my_data)
        await ep.close()
        self.lf.close()

    def get_node_ip(self):
        """Returns the IP address of the current node."""
        return ray.services.get_node_ip_address()

@ray.remote(num_gpus=1)
class Client:
    def __init__(self):
        # Initialize PyTorch
        _ = torch.rand(1, dtype=torch.float, device='cuda')
    async def run_concurrent(self):
        # Wait server finishs initialization
        time.sleep(5)
        # Start client endpoint
        ep = await ucp.create_endpoint(host, port)
        msg = torch.empty(n_elements, dtype=torch.float, device='cuda') # create some data to send

        print("Receive data from server")
        await ep.recv(msg)
        await ep.close()
        print("client data:", msg)

if __name__ == "__main__":
    ray.init()
    server = Server.remote()
    server_coroutine = server.run_concurrent.remote()
    client = Client.remote()
    client_coroutine = client.run_concurrent.remote()
    ray.get([server_coroutine, client_coroutine])
