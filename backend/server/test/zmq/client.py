import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
socket.send(b"Hello")
#  Get the reply.
message = socket.recv()
print(f"Received reply [ {message} ]")
