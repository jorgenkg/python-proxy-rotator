import argparse
from server import ThreadedPipeServer

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--local_proxies', action='store_true')
parser.add_argument('-f', '--force_proxy_refresh', action='store_true')
parser.add_argument('-n', '--chainlength')
args = parser.parse_args()

proxy = ThreadedPipeServer(
            try_local_proxylist = False if args.force_proxy_refresh and not args.local_proxies else True,
            chainlength = args.chainlength
        )
try:
    print "\nServer is running."
    proxy.serve_forever()
except KeyboardInterrupt:
    print "\nServer is shuting down. \nPlease wait for the called requests to terminate."
    proxy.stop_proxy()
    proxy.server_close()
