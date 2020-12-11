import os
import random

import cherrypy
"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#B765CD",  # TODO: Personalize
            "head": "default",  # TODO: Personalize
            "tail": "default",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    def willCollideWithSelf(self, data, direction):
        head = data['you']['head']

        if direction == "up" and {
                'x': head['x'],
                'y': head['y'] + 1
        } in data['you']['body']:
            return True
        elif direction == "down" and {
                'x': head['x'],
                'y': head['y'] - 1
        } in data['you']['body']:
            return True
        elif direction == "right" and {
                'x': head['x'] + 1,
                'y': head['y']
        } in data['you']['body']:
            return True
        elif direction == "left" and {
                'x': head['x'] - 1,
                'y': head['y']
        } in data['you']['body']:
            return True

        return False

    def willGoOutOfBounds(self, data, direction):
        head = data['you']['head']

        if direction == "up" and head['y'] == data['board']['height'] - 1:
            return True
        elif direction == "down" and head['y'] == 0:
            return True
        elif direction == "right" and head['x'] == data['board']['width'] - 1:
            return True
        elif direction == "left" and head['x'] == 0:
            return True

        return False

    def willHitAnotherSnake(self, data, direction):
        head = data['you']['head']
        your_health = data['you']['health']
        for snake in data['board']['snakes']:
            opponent_body = snake['body']
            opponent_head = snake['body'][0]
            opponent_health = snake['health']
            if direction == "up" and {
                    'x': head['x'],
                    'y': head['y'] + 1
            } in opponent_body:
                if head['x'] == opponent_head[
                        'x'] and head['y'] + 1 == opponent_head[
                            'y'] and your_health > opponent_health:
                    #there's a h2h collision and an opportunity to eliminate opponent
                    return False
                return True
            elif direction == "down" and {
                    'x': head['x'],
                    'y': head['y'] - 1
            } in opponent_body:
                if head['x'] == opponent_head[
                        'x'] and head['y'] - 1 == opponent_head[
                            'y'] and your_health > opponent_health:
                    return False
                return True
            elif direction == "right" and {
                    'x': head['x'] + 1,
                    'y': head['y']
            } in opponent_body:
                if head['x'] + 1 == opponent_head['x'] and head[
                        'y'] == opponent_head[
                            'y'] and your_health > opponent_health:
                    return False
                return True
            elif direction == "left" and {
                    'x': head['x'] - 1,
                    'y': head['y']
            } in opponent_body:
                if head['x'] - 1 == opponent_head['x'] and head[
                        'y'] == opponent_head[
                            'y'] and your_health > opponent_health:
                    return False
                return True
        return False

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json
        print("data is:****************", data)
        print("data is:****************")
        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        random.shuffle(possible_moves)

        move = -1
        moves_data = {
        }  # stores data for all 4 directions with their values for will_hit_another_snake and will_go_out_of_bounds
        total_safe_moves = 0
        for possible_move in possible_moves:
            will_hit_another_snake = self.willHitAnotherSnake(
                data, possible_move)
            will_go_out_of_bounds = self.willGoOutOfBounds(data, possible_move)
            moves_data[possible_move] = {
                'will_hit_another_snake': will_hit_another_snake,
                'will_go_out_of_bounds': will_go_out_of_bounds,
            }
            if not will_hit_another_snake and not will_go_out_of_bounds:
                total_safe_moves += 1

        # print("moves data: ", moves_data)
        # print("total_safe_moves: ", total_safe_moves)

        safe_move_number = 1
        while move == -1 and safe_move_number <= total_safe_moves:
            move = self.getSafeMoveNumberXFromList(moves_data,
                                                   safe_move_number)
            print("from list got the move as : ", move)
            # if move != -1 and self.isCollisionPossibleInNxtStep(data, move):
            #     move = -1
            #     print("move decided does not look safe for next step")
            
            safe_move_number += 1

        if move == -1:
            move = random.choice(possible_moves)

        print(f"MOVE: {move}")
        return {"move": move}

    def getSafeMoveNumberXFromList(self, moves_data, safe_move_number):
        # print("counter received as : ", safe_move_number)
        move = -1
        i = 0
        for key in moves_data:
            will_hit_another_snake = moves_data[key]['will_hit_another_snake']
            will_go_out_of_bounds = moves_data[key]['will_go_out_of_bounds']
            if not will_hit_another_snake and not will_go_out_of_bounds:
                i += 1
                if safe_move_number == i:
                    move = key
                    break
        return move

    def isCollisionPossibleInNxtStep(self, data, decided_move):
        head = data['you']['head']
        head_at_next_step = {'x': head['x'], 'y': head['y']}
        if decided_move == "up":
            head_at_next_step['y'] += 1
        if decided_move == "down":
            head_at_next_step['y'] -= 1
        if decided_move == "right":
            head_at_next_step['x'] += 1
        if decided_move == "left":
            head_at_next_step['x'] -= 1
        temp_data = data
        temp_data['you']['head'] = head_at_next_step
        possible_moves = ["up", "down", "left", "right"]
        collision_possible = False
        for p_m in possible_moves:
            if self.willHitAnotherSnake(temp_data, p_m):
                collision_possible = True
                break
        return collision_possible

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update({
        "server.socket_port":
        int(os.environ.get("PORT", "8080")),
    })
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
