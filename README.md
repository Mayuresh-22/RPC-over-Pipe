# RPC over Pipe
It is lightweight local RPC (Remote Procedure Call) system implemented over Linux named pipe.


## What is RPC?

RPC or Remote Procedure Call is a communication paradigm where one program/process calls a function/service that actually gets execute in different process(or even a different machine). The caller doesn't need to know the implementation details of the called function it just feels like a local function call to the caller.


## How RPC over Pipe works?

1. Server advertises the available services to the client by writing it to a named pipe.
2. Client picks the service, and serializes service name + args + kwargs into JSON (wire format) and writes to pipe.
3. Server executes it, and writes back the result to the client.

Note: Communication happens via single named pipe.


## What's next?

- Support multiple concurrent clients
- Support async/non-blocking calls
