import socket
import json
from random import randrange


class Player:
    def __init__(self, user_id, address, position, items: list):
        self.game_id = None
        self.user_id = user_id
        self.address = address

        self.spawn_position = None
        self.position = position
        self.items = items
        self.last_attacker = None
        self.texture = 0
        self.score = 0
        self.health = 100

    def update(self, message) -> dict:
        data = {"msg": "game_data", "user_id": self.user_id, "score": self.score}
        for i, j in message.items():
            if i == "position":
                self.position = j
                data["position"] = j
            elif i == "texture":
                self.texture = j
                data["texture"] = j
            elif i == "last_attacker":
                self.last_attacker = j
            elif i == "items":
                p_ids = []
                data["items"] = []
                for p_id, p_type, p_pos in j:
                    p_ids.append(p_id)
                    if p_id not in self.items:
                        data["items"].append((p_type, p_pos))
                self.items = p_ids
            elif i == "health":
                data["health"] = j
                self.health = j
        return data

    def send(self, encoded_data):
        """
        Send to address given data, data are received encoded to avoid any encode repetition
        :param encoded_data:
        :return:
        """
        server.socket.sendto(encoded_data, self.address)


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

            elif message["msg"] == "game_data":
                user = self.users[message["user_id"]]
                data = user.update(message)
                if user.health <= 0:
                    if user.last_attacker is not None:
                        self.users[user.last_attacker].score += 1

                        if self.users[user.last_attacker].score > 3:
                            self.end_game(self.users[user.last_attacker].game_id)

                    self.spawn(user)
                else:
                    users = list(
                        filter(lambda x: x != user.user_id, self.games[user.game_id]))
                    data = json.dumps(data).encode()
                    for user in users:
                        self.users[user].send(data)

    def start_game(self):
        game = randrange(10000000)
        spawn_positions = [(400, 100), (700, 100)]

        users = self.queue.pop(0), self.queue.pop(0)
        self.games[game] = users
        data = {"msg": "start", "players": users}
        data = json.dumps(data).encode()

        for user_id in users:
            user = self.users[user_id]

            user.spawn_position = spawn_positions.pop()
            user.game_id = game
            user.send(data)
            self.spawn(user)

    def spawn(self, user: Player):
        data = {"msg": "spawn", "position": user.spawn_position}
        user.send(json.dumps(data).encode())

    def end_game(self, game_id: int):
        users = self.games[game_id]
        data = json.dumps({"msg": "end"}).encode()
        for user in users:
            self.users[user].send(data)


if __name__ == '__main__':
    server = Server()
    server.start()
