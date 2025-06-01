# ================= SERVER1.PY (Death Removal Logic) =================
import socket
import threading
import main_game
from main_game import get_random_spawn
PORT = 5555
HOST = '0.0.0.0'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"Server started on {HOST}:{PORT}")

clients_lock = threading.Lock()
clients = {}

players_lock = threading.Lock()
players = {}

platforms = main_game.create_platforms()

def handle_client(client, addr):
    print(f"New connection {addr} connected")

    while True:
        try:
            msg = client.recv(1024)
            if not msg:
                continue  # Don't break immediately; wait for actual disconnect
            msg = msg.decode("utf-8")

            if msg.startswith('GAME'):
                with players_lock:
                    if addr not in players:
                        continue

                    player = players[addr]
                    player.state = "idle"
                    direction_updated = False

                    if "RIGHT" in msg:
                        player.rect.x += player.speed
                        player.state = "run"
                        player.direction = "right"
                        direction_updated = True
                    if "LEFT" in msg:
                        player.rect.x -= player.speed
                        player.state = "run"
                        player.direction = "left"
                        direction_updated = True
                    if "UP" in msg:
                        player.jump()
                        player.state = "jump"
                    if "PUNCH" in msg:
                        player.state = "punch"
                        for other_addr, other_player in players.items():
                            if other_addr != addr and player.rect.colliderect(other_player.rect):
                                other_player.health = max(0, other_player.health - 2)

                    if not direction_updated and not hasattr(player, 'direction'):
                        player.direction = "right"

                    player.move(platforms)
                    player.rect.x = max(0, min(player.rect.x, 1230))
                    player.rect.y = max(0, min(player.rect.y, 670))

                    # Remove dead players
                    to_remove = [a for a, p in players.items() if p.health <= 0]
                    for dead_addr in to_remove:
                        if dead_addr in clients:
                            try:
                                clients[dead_addr].close()
                            except:
                                pass
                            del clients[dead_addr]
                        if dead_addr in players:
                            del players[dead_addr]

                broadcast_positions()

        except Exception as e:
            print(f"Error with {addr}: {e}")
            break

    with clients_lock:
        if addr in clients:
            del clients[addr]
    with players_lock:
        if addr in players:
            del players[addr]

    client.close()
    broadcast_positions()

def broadcast_positions():
    with players_lock:
        message = "UPDATE"
        for addr, player in players.items():
            x, y = player.rect.x, player.rect.y
            state = player.state
            health = player.health
            direction = getattr(player, 'direction', 'right')
            message += f" {addr[0]}:{addr[1]}:{x},{y},{state},{health},{direction}"

    with clients_lock:
        for client in clients.values():
            try:
                client.sendall(message.encode())
            except Exception as e:
                print(f"Error sending to client: {e}")

def accept_clients():
    while True:
        try:
            client, addr = server.accept()
            print(f"New connection from {addr}")

            with clients_lock:
                clients[addr] = client

            with players_lock:
                spawn_x, spawn_y = get_random_spawn(platforms)
                p = main_game.Player(str(addr), spawn_x, spawn_y)
                p.health = 100
                p.direction = "right"
                players[addr] = p

            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.daemon = True
            thread.start()

            broadcast_positions()

        except Exception as e:
            print(f"Error accepting client: {e}")

try:
    accept_clients()
except KeyboardInterrupt:
    print("\nServer shutting down...")
    server.close()
