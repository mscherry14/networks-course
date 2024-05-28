import json
import sys

from time import sleep
from threading import Thread
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS

MAX_NUMBER_OF_HOPS = 20
MAX_NUMBER_OF_ROUTERS = 30
TIME_BETWEEN_UPDATES = 3 
NEED_STEPS = False
CONFIG = "config.json"

table_title = "Final state of router {ip} table:"
table_headers = ["Source IP", "Destination IP", "Next Hop", "Metric"]
table_headers_align = ["l", "l", "l", "r"]
perineal_table_title = "Simulation step {step} of router {ip}"


def update_table(router):
    is_updated = False
    a = ip_to_id_map[router]
    for e in config:
        u, v = e
        if router != u and router != v:
            continue

        if router == v:
            u, v = v, u

        b = ip_to_id_map[v]
        for i in range(MAX_NUMBER_OF_ROUTERS):
            if routes[a][i] > routes[b][i] + 1:
                routes[a][i] = routes[b][i] + 1
                next_hop[a][i] = v
                is_updated = True
    return is_updated


def format_table(router, step=-1):
    if step == -1:
        result = table_title.format(ip=router)
    else:
        result = perineal_table_title.format(ip=router, step=step)
    table = PrettyTable(table_headers)
    table.set_style(PLAIN_COLUMNS)
    for i in range(len(table_headers)):
        table.align[table_headers[i]] = table_headers_align[i]
    a = ip_to_id_map[router]
    for ip in ip_to_id_map:
        if ip == router:
            continue
        b = ip_to_id_map[ip]
        table.add_row([router, ip, next_hop[a][b], routes[a][b]])
    result = result + "\n" + table.get_string()  + "\n"
    return result


def run_rip(router):
    last = ""
    for i in range(MAX_NUMBER_OF_HOPS):
        is_updated = update_table(router)
        if not is_updated:
            print(format_table(router))
            break
        if NEED_STEPS:
            table = format_table(router, step=i)
            print(table)
        sleep(TIME_BETWEEN_UPDATES)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--steps" or sys.argv[1] == "-s":
            NEED_STEPS = True
    with open(CONFIG, "r") as f:
        config = json.loads(f.read())

    ip_to_id_map = dict()
    for e in config:
        u, v = e
        if u not in ip_to_id_map.keys():
            ip_to_id_map[u] = len(ip_to_id_map)
        if v not in ip_to_id_map.keys():
            ip_to_id_map[v] = len(ip_to_id_map)
    
    if len(ip_to_id_map) > MAX_NUMBER_OF_ROUTERS:
        print("MAX_NUMBER_OF_ROUTERS exceeded: network too large")

    id_to_ip_map = dict()
    for ip in ip_to_id_map:
        id_to_ip_map[ip_to_id_map[ip]] = ip

    routes = [[MAX_NUMBER_OF_HOPS + 1] * MAX_NUMBER_OF_ROUTERS for i in range(MAX_NUMBER_OF_ROUTERS)]
    next_hop = [["unknown"] * MAX_NUMBER_OF_ROUTERS for i in range(MAX_NUMBER_OF_ROUTERS)]

    for i in range(MAX_NUMBER_OF_ROUTERS):
        routes[i][i] = 0
        next_hop[i][i] = id_to_ip_map.get(i, None)

    threads = [Thread(target=run_rip, args=(router,)) for router in ip_to_id_map]

    for router in ip_to_id_map:
        threads[ip_to_id_map[router]].start()

    for thread in threads:
        thread.join()
