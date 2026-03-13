import json
import os
import sys

import requests as rq

print("LOCAL RPC SERVER PROCESS")

class Services:
    """
    A collection of services that the RPC server can provide.
    """
    def ping(self):
        return "Pong!"
    
    def info(self):
        return {
            "name": "Local RPC",
            "version": "1.0",
            "status": "Running...",
            "cpu_count": os.cpu_count()
		}

    def get_public_ip(self):
        return rq.get("https://api.ipify.org").text

    def get_html(self, url):
        html = rq.get(url).text
        return html


class RPCServer:
    """
    A simple lightweight local server that advertises available services and listens for incoming RPC calls from clients.

    It uses a single named pipe for communication.
    """
    COMMON_QUEUE = "req_res_queue"

    def __init__(self):
        services = Services()
        self.services = {
			service_name: getattr(services, service_name) for service_name in dir(services) if not service_name.startswith("__")
		}
        self.available_services = list(self.services.keys()) + ["disconnect"]
        self.DISCONNECT_FLAG = False
    
    def call(self, service_name, *args, **kwargs):
        if service_name not in self.services:
            raise ValueError(f"Service '{service_name}' not found.")
        service = self.services[service_name]
        return service(*args, **kwargs)

    def start(self):
        with open(self.COMMON_QUEUE, "w") as rrq:
            rrq.write(json.dumps({"services": self.available_services})+"\n")
        
        print("Available services:")
        for service in self.available_services:
            print(f"- {service}")
        print("\nReady to receive requests...")

        while True:
            with open(self.COMMON_QUEUE, "r") as rrq:
                reqs = rrq.read().splitlines()
                reqs = [
                    json.loads(req) for req in reqs  # request structure: {service: <service_name>, args: [...], kwargs: {...}}
                ]
                for req in reqs:
                    try:
                        service_name = req.get("service")
                        args = req.get("args", [])
                        kwargs = req.get("kwargs", {})
                        print(f"RECEIVED: call request for {service_name} with args={args} and kwargs={kwargs}")
                        
                        if service_name == "disconnect":
                            self.DISCONNECT_FLAG = True
                            break

                        # call the service and write the result back to the queue
                        result = self.call(service_name, *args, **kwargs)
                        with open(self.COMMON_QUEUE, "a") as rrq:
                            rrq.write(json.dumps({"service": service_name, "result": result})+"\n")
                        print(f"PROCESSED: call request of {service_name}.\n")
                    except Exception as e:
                        with open(self.COMMON_QUEUE, "a") as rrq:
                            rrq.write(json.dumps({"error": str(e)})+"\n")
                    except KeyboardInterrupt as e:
                        print("Shutting down server...")
                        sys.exit(0)
            
            if self.DISCONNECT_FLAG:
                print("\nSESSION DISCONNECTED. Restarting server...")
                self.DISCONNECT_FLAG = False
                with open(self.COMMON_QUEUE, "w") as rrq:
                    rrq.write(json.dumps({"services": self.available_services})+"\n")
                print("Ready to receive requests...\n")


if __name__ == "__main__":
    rpc_server = RPCServer()
    rpc_server.start()
