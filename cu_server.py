import asyncio
import time
import ucp
import cupy as cp

n_bytes = 2**30
host = ucp.get_address(ifname='lo')  # ethernet device name
port = 13337

async def send(ep):
    # recv buffer
    arr = cp.empty(n_bytes, dtype='u1')
    await ep.recv(arr)
    assert cp.count_nonzero(arr) == cp.array(0, dtype=cp.int64)
    print("Received CuPy array")

    # increment array and send back
    arr += 1
    print("Sending incremented CuPy array")
    await ep.send(arr)

    await ep.close()
    lf.close()

async def main():
    global lf
    lf = ucp.create_listener(send, port)

    while not lf.closed():
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())

