import socket
import json
import sys

def send_request(req_dict):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 25002))
        sock.sendall(json.dumps(req_dict).encode())
        data = sock.recv(8192).decode()
        return json.loads(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python client.py stats top [limit]")
        print("  python client.py stats agents")
        print("  python client.py stats hourly [YYYYMMDDHH]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'stats':
        if len(sys.argv) < 3:
            print("Missing stats subcommand: top, agents, hourly")
            sys.exit(1)
        sub = sys.argv[2]
        req = {"action": "wiki_stats"}
        if sub == 'top':
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            req["query_type"] = "top_articles"
            req["limit"] = limit
            resp = send_request(req)
            for row in resp:
                print(f"{row['title']}: {row['views']} views")
        elif sub == 'agents':
            req["query_type"] = "agent_breakdown"
            resp = send_request(req)
            for row in resp:
                print(f"{row['agent']}: {row['views']} views")
        elif sub == 'hourly':
            hour = sys.argv[3] if len(sys.argv) > 3 else None
            req["query_type"] = "hourly_stats"
            req["hour"] = hour
            resp = send_request(req)
            for row in resp:
                print(f"{row['hour']}: {row['views']} views")
        else:
            print("Unknown stats subcommand")
    else:
        print("Unknown command")
