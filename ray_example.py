import asyncio
import time
import ucp
import torch
import numpy as np
import ray

n_bytes = 2**30
host = "127.0.0.1"
port = 13337

@ray.remote(num_gpus=1)
class Server:
    async def run_concurrent(self):
        self.my_data = torch.rand(10)
        print("server data:", self.my_data)
        self.lf = ucp.create_listener(self.call_back, port)
        while not self.lf.closed():
            await asyncio.sleep(0.1)

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

@ray.remote(num_gpus=1)
class Client:
    async def run_concurrent(self):
        time.sleep(2)
        ep = await ucp.create_endpoint(host, port)
        msg = np.zeros(n_bytes, dtype='u1') # create some data to send
        msg_size = np.array([msg.nbytes], dtype=np.uint64)

        # send message
        print("Send Original NumPy array")
        await ep.send(msg, msg_size)  # send the real message

        # recv response
        print("Receive Incremented NumPy arrays")
        resp = np.empty_like(msg)
        await ep.recv(resp, msg_size)  # receive the echo
        await ep.close()
        np.testing.assert_array_equal(msg + 1, resp)

if __name__ == "__main__":
    ray.init()
    server = Server.remote()
    server_coroutine = server.run_concurrent.remote()
    client = Client.remote()
    client_coroutine = client.run_concurrent.remote()
    ray.get([server_coroutine, client_coroutine])
