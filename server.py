import asyncio
import time
import ucp
import numpy as np

n_bytes = 2**30
host = ucp.get_address(ifname='lo')  # ethernet device name
port = 13337

async def send(ep):
    # recv buffer
    arr = np.empty(n_bytes, dtype='u1')
    await ep.recv(arr)
    assert np.count_nonzero(arr) == np.array(0, dtype=np.int64)
    print("Received NumPy array")

    # increment array and send back
    arr += 1
    print("Sending incremented NumPy array")
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
