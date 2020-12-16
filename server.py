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

    def isHeadToHeadPossible(self, your_head_next_pos, opponent_head):
        # check if opponent is 1 away from your_head_next_pos
        if opponent_head['x'] == your_head_next_pos['x'] and abs(opponent_head['y'] - your_head_next_pos['y']) == 1:
          return True
        elif opponent_head['y'] == your_head_next_pos['y'] and abs(opponent_head['x'] - your_head_next_pos['x']) == 1:
          return True
        return False

    def checkForHeadToHead(self, data, direction):
        head = data['you']['head']
        your_length = data['you']['length']
        for snake in data['board']['snakes']:
            if snake['id'] == data['you']['id']:
              continue
            opponent_body = snake['body']
            opponent_head = snake['body'][0]
            opponent_length = snake['length']
            if direction == "up":
                new_pos = {'x': head['x'], 'y': head['y'] + 1}
            elif direction == "down":
                new_pos = {'x': head['x'],'y': head['y'] - 1}
            elif direction == "right":
                new_pos = {'x': head['x'] + 1,'y': head['y']}
            elif direction == "left":
                new_pos = {'x': head['x'] - 1,'y': head['y']}
            if self.isHeadToHeadPossible(new_pos, opponent_head):
                if your_length <= opponent_length:
                    return "defeat"
                else:
                    return "eliminate"
        return "not_possible"

    def willHitAnotherSnake(self, data, direction):
        head = data['you']['head']
        your_length = data['you']['length']
        for snake in data['board']['snakes']:
            # if snake['id'] != data['you']['id']:
            opponent_body = snake['body']
            opponent_head = snake['body'][0]
            opponent_length = snake['length']
            print(f"head: {head}")
            print(f"opponent {opponent_body}")
            if direction == "up":
                new_pos = {'x': head['x'], 'y': head['y'] + 1}
                if new_pos in opponent_body:
                    if data['turn'] <2 or new_pos != opponent_body[len(opponent_body)-1]:
                        return True
                # elif snake['id'] != data['you']['id'] and self.isHeadToHeadPossible(new_pos, opponent_head) and your_length <= opponent_length:
                #     #there's a h2h collision and an opportunity to eliminate opponent
                #     return True
            elif direction == "down":
                new_pos = {'x': head['x'],'y': head['y'] - 1}
                if new_pos in opponent_body:
                    if data['turn'] <2 or new_pos != opponent_body[len(opponent_body)-1]:
                        return True
                # elif snake['id'] != data['you']['id'] and self.isHeadToHeadPossible(new_pos, opponent_head) and your_length <= opponent_length:
                #     return True
            elif direction == "right":
                new_pos = {'x': head['x'] + 1,'y': head['y']}
                if new_pos in opponent_body:
                    if data['turn'] <2 or new_pos != opponent_body[len(opponent_body)-1]:
                        return True
                # elif snake['id'] != data['you']['id'] and self.isHeadToHeadPossible(new_pos, opponent_head) and your_length <= opponent_length:
                #     return True
            elif direction == "left":
                new_pos = {'x': head['x'] - 1,'y': head['y']}
                if new_pos in opponent_body:
                    if data['turn'] <2 or new_pos != opponent_body[len(opponent_body)-1]:
                        return True
                # elif snake['id'] != data['you']['id'] and self.isHeadToHeadPossible(new_pos, opponent_head) and your_length <= opponent_length:
                #     return True
        return False

    def getDistanceToFood(self, foodPos, head):
      return abs(foodPos['x'] - head['x']) + abs(foodPos['y'] - head['y'])

    def findNearestFood(self, data):
      if len(data['board']['food']) == 0:
        return None

      nearest = data['board']['food'][0]
      minDistance = self.getDistanceToFood(data['board']['food'][0], data['you']['head'])

      for food in data['board']['food']:
        curDistance = self.getDistanceToFood(food, data['you']['head'])
        if minDistance > curDistance:
          nearest = food
          minDistance = curDistance
      return nearest

    #TODO: decide on strategy for when to eat
    # when health is less than a certain amount?
    # maybe always so we can try to starve the other snakes?
    def shouldEat(self, data):
      print(f"health: {data['you']['health']}")
      if data['you']['health'] < 40:
        return True
      return False

    def canMoveInDirection(self, data, direction):
      print(f"checking direction {direction} with data:")
      will_hit_another_snake = self.willHitAnotherSnake(
          data, direction)
      will_go_out_of_bounds = self.willGoOutOfBounds(data, direction)
      will_lose_head2head = self.checkForLostHeadToHead(data, direction)
      if not will_hit_another_snake and not will_go_out_of_bounds:
        return True
      return False

    def getDirectionsToGoToEat(self, data):
      nearestFood = self.findNearestFood(data)
      if nearestFood is not None:
        print(f"there is food at: {nearestFood}")

        direction_to_eat_data = {
          "up": False, "down": False, "left": False, "right": False
        }
        shouldGoUp = False
        shouldGoRight = False
        shouldGoLeft = False
        shouldGoDown = False
        
        if nearestFood['x'] > data['you']['head']['x']:
          # need to move right
          shouldGoRight = True
          direction_to_eat_data["right"] = True
          print("1")
        elif nearestFood['x'] < data['you']['head']['x']:
          # need to move left
          shouldGoLeft = True
          direction_to_eat_data["left"] = True
          print("2")
        if nearestFood['y'] > data['you']['head']['y']:
          # need to move up
          shouldGoUp = True
          direction_to_eat_data["up"] = True
          print("3")
        elif nearestFood['y'] < data['you']['head']['y']:
          # need to move down
          shouldGoDown = True
          direction_to_eat_data["down"] = True
          print("4")
        
        return direction_to_eat_data
        
        # if shouldGoRight and self.canMoveInDirection(data, "right"):
        #   return "right"
        # elif shouldGoLeft and self.canMoveInDirection(data, "left"):
        #   return "left"
        # elif shouldGoUp and self.canMoveInDirection(data, "up"):
        #   return "up"
        # elif shouldGoDown and self.canMoveInDirection(data, "down"):
        #   return "down"
        # return None

    def getBestMove(self, moves_data, data, possible_moves):
        okay_moves = []
        # get moves that won't go out of bounds or hit another snake
        for move in moves_data:
            if not moves_data[move]['will_go_out_of_bounds'] and not moves_data[move]['will_hit_another_snake']:
                okay_moves.append(move)

        if len(okay_moves) == 0:
            print("************* making a random move ****************")
            random.choice(possible_moves)
        
        best_moves = []

        # if there is a move that will eliminate another snake, do that
        for move in okay_moves:
            if moves_data[move]['head2head_result'] == "eliminate":
                return move
            elif moves_data[move]['head2head_result'] == "not_possible":
                best_moves.append(move)

        #determine if we should eat
        if self.shouldEat(data):
            print("GO EAT")
            direction_to_eat_data = self.getDirectionsToGoToEat(data)
            if direction_to_eat_data["right"] is True and "right" in best_moves:
                return "right"
            if direction_to_eat_data["left"] is True and "left" in best_moves:
                return "left"
            if direction_to_eat_data["up"] is True and "up" in best_moves:
                return "up"
            if direction_to_eat_data["down"] is True and "down" in best_moves:
                return "down"

        # now we know that we can't eliminate another player
        # get first move in order that won't risk elimination
        if len(best_moves) > 0:
            for move in possible_moves:
                if move in best_moves:
                    return move

        for move in possible_moves:
            if move in okay_moves:
                return move
        
        return okay_moves[0]


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]

        print("data is:****************")
        print(data)
        print("****************")

        moves_data = {
          "up": {}, "down": {}, "left": {}, "right": {}
        }
        for possible_move in possible_moves:
            will_go_out_of_bounds = self.willGoOutOfBounds(data, possible_move)
            if not will_go_out_of_bounds:
                will_hit_another_snake = self.willHitAnotherSnake(data, possible_move)
                head2head_result = self.checkForHeadToHead(data, possible_move)
                moves_data[possible_move] = {
                  'will_hit_another_snake': will_hit_another_snake,
                  'will_go_out_of_bounds': will_go_out_of_bounds,
                  'head2head_result' : head2head_result
                }
            else:
              moves_data[possible_move] = {
                'will_hit_another_snake': True,
                'will_go_out_of_bounds': will_go_out_of_bounds,
                'head2head_result' : "not_possible"
              }

        move = self.getBestMove(moves_data, data, possible_moves)

        print(f"MOVE: {move}")
        return {"move": move}

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
