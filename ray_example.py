import asyncio
import time
import ucp
import torch
import ray

n_bytes = 2**30
port = 13337

@ray.remote(num_gpus=1)
class Server:
    def __init__(self):
        my_data = torch.rand(10)
        print("server data:", my_data)

    def send(self):
        print("send")

if __name__ == "__main__":
    ray.init()
    server = Server.remote()

