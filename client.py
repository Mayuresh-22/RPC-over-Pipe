import json

print("LOCAL RPC CLIENT PROCESS")

class RPCClient:
    """A simple client that connects to the local RPC server and allows users to call available services.
    
    It uses a single named pipe for communication.
    """
    COMMON_QUEUE = "req_res_queue"

    def connect(self):
        print("CONNECTING to the server...")
        with open(self.COMMON_QUEUE, "r") as rrq:
            data = rrq.read().splitlines()  # blocks until there is data to read
            self.available_services = data[0] if data else None

            if self.available_services:
                self.available_services = (
                    json.loads(self.available_services)
                    .get("services", [])
                )
                if self.available_services is None:
                    print("Failed to parse available services.")
                    self.available_services = None
                    return
                print("CONNECTED.\nGot Available services from server:")
                for service in self.available_services:
                    print(f"- {service}")
                print()
            else:
                print("No available services found.")
                self.available_services = None
    
    def call(self, service_name, *args, **kwargs):
        if service_name not in self.available_services:
            print(f"Unknown service '{service_name}' is called. Check available services.\n")
            return

        # serialize the call and send RPC request
        print(f"CALL: calling service: {service_name}")
        call_request = {"service": service_name, "args": args, "kwargs": kwargs}
        with open(self.COMMON_QUEUE, "w") as rrq:
            rrq.write(json.dumps(call_request)+"\n")
        
        if service_name == "disconnect":  
            # as disconnect is a special service that makes
            # server to restart the session, we can just exit the client
            print("DISCONNECTED: from the server.\n")
            exit(0)
        
        # immediately read/wait for the result of the call
        with open(self.COMMON_QUEUE, "r") as rrq:
            results = rrq.read().splitlines()  # blocks until there is data to read
            results = [
                json.loads(result) for result in results
            ]

            for res in results:  # can be multiple results seperated by \n
                service_name = res.get("service", None)
                result = res.get("result", None)
                error = res.get("error", None)

                if error:
                    print(f"ERROR: {error}")

                print(f"RESULT: ({service_name}): {result}\n")


def process_kwargs(kwargs: list[str]) -> dict[str, str]:
    """
    Helper function to process kwargs from user input.

    Expected format: key=value, key2=value2, ...
    """
    processed_kwargs: dict[str, str] = {}
    for kwarg in kwargs:
        if kwarg:
            kwarg = kwarg.strip().split("=")
            processed_kwargs[kwarg[0].strip()] = kwarg[1].strip() if len(kwarg) > 1 else ""
    return processed_kwargs


def process_args(args: list[str]) -> list[str]:
    """
    Helper function to process args from user input.

    Excpected format: arg1, arg2, arg3, ...
    """
    processed_args: list[str] = []
    for arg in args:
        if arg:
            processed_args.append(arg)
    return processed_args


if __name__ == "__main__":
    rpc_client = RPCClient()
    rpc_client.connect()

    if rpc_client.available_services:
        while(True):
            service_name = input("service name: ")
            args = input("args (comma seperated): ").strip().split(",")
            kwargs = input("kwargs (comma seperated): ").strip().split(",")
            rpc_client.call(service_name, *process_args(args), **process_kwargs(kwargs))
