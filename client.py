import asyncio
import ucp
import numpy as np

port = 13337
n_bytes = 2**30

async def main():
    host = ucp.get_address(ifname='lo')  # ethernet device name
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

if __name__ == '__main__':
    asyncio.run(main())

