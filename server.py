import socket
import json
from random import randrange


class Player:
    def __init__(self, user_id, address, position, projectiles: list):
        self.user_id = user_id
        self.game_id = None
        self.address = address
        self.position = position
        self.projectiles = projectiles
        self.texture = 0
        self.score = 0

    def update(self, message) -> dict:
        data = {"msg": "game_data", "user_id": self.user_id}
        for i, j in message.items():
            if i == "position":
                self.position = j
                data["position"] = j
            elif i == "texture":
                self.texture = j
                data["texture"] = j
            elif i == "projectiles":
                p_ids = []
                data["projectiles"] = []
                for p_id, p_type, p_pos in j:
                    p_ids.append(p_id)
                    if p_id not in self.projectiles:
                        data["projectiles"].append((p_type, p_pos))
                self.projectiles = p_ids
            elif i == "health":
                data["health"] = j
        return data


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
        self.users = {}
        self.games = {}
        self.queue = []

    def start(self):
        self.socket.bind(("127.0.0.1", 4444))

        while True:
            message, address = self.socket.recvfrom(1024)
            message = json.loads(message)
            if message["msg"] == "play":
                self.queue.append(message["user_id"])
                self.users[message["user_id"]] = Player(message["user_id"], address, (100, 100), [])

                if len(self.queue) == 2:
                    self.start_game()
                    self.start_new_round(self.users[message["user_id"]].game_id)

            elif message["msg"] == "game_data":
                user = self.users[message["user_id"]]
                data = user.update(message)
                if data["health"] <= 0:
                    self.start_new_round(user.game_id)
                else:
                    users = list(
                        filter(lambda x: x != user.user_id, self.games[user.game_id]))

                    for user in users:
                        self.socket.sendto(json.dumps(data).encode(), self.users[user].address)

    def start_game(self):
        game = randrange(10000000)
        users = self.queue.pop(0), self.queue.pop(0)
        self.games[game] = users
        data = {"msg": "start", "players": users}
        for user_id in users:
            self.users[user_id].game_id = game
            self.socket.sendto(json.dumps(data).encode(), self.users[user_id].address)

    def start_new_round(self, game_id: int):
        coords = [(400, 100), (700, 100)]
        data = {"msg": "new_round", "health": 100, "texture": 0}
        for user in self.games[game_id]:
            data["position"] = coords.pop()
            self.socket.sendto(json.dumps(data).encode(), self.users[user].address)


if __name__ == '__main__':
    Server().start()
