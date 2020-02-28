import asyncio
import time
import ucp
import torch
import numpy as np
import ray

n_bytes = 2**30
port = 13337

@ray.remote(num_gpus=1)
class Server:
    def __init__(self):
        self.my_data = torch.rand(10)
        print("server data:", self.my_data)
        self.lf = ucp.create_listener(self.call_back.remote, port)

    async def call_back(self, ep):
        arr = np.empty(n_bytes, dtype='u1')
        await ep.recv(arr)
        assert np.count_nonzero(arr) == np.array(0, dtype=np.int64)
        print("Received NumPy array")

        # increment array and send back
        arr += 1
        print("Sending incremented NumPy array")
        await ep.send(arr)
        await ep.close()

    def get_node_ip(self):
        """Returns the IP address of the current node."""
        return ray.services.get_node_ip_address()

if __name__ == "__main__":
    ray.init()
    server = Server.remote()
    ray.get(server)
