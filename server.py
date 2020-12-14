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
            "color": "#0b03fc",  # TODO: Personalize
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
      will_hit_another_snake = self.willHitAnotherSnake(
          data, direction)
      will_go_out_of_bounds = self.willGoOutOfBounds(data,    direction)
      if not will_hit_another_snake and not will_go_out_of_bounds:
        return True
      return False

    def getDirectionToGoToEat(self, data):
      nearestFood = self.findNearestFood(data)
      if nearestFood is not None:
        print(f"there is food at: {nearestFood}")
        shouldGoUp = False
        shouldGoRight = False
        shouldGoLeft = False
        shouldGoDown = False
        
        if nearestFood['x'] > data['you']['head']['x']:
          # need to move right
          shouldGoRight = True
          print("1")
        elif nearestFood['x'] < data['you']['head']['x']:
          # need to move left
          shouldGoLeft = True
          print("2")
        if nearestFood['y'] > data['you']['head']['y']:
          # need to move up
          shouldGoUp = True
          print("3")
        elif nearestFood['y'] < data['you']['head']['y']:
          # need to move down
          shouldGoDown = True
          print("4")
        
        if shouldGoRight and self.canMoveInDirection(data, "right"):
          return "right"
        elif shouldGoLeft and self.canMoveInDirection(data, "left"):
          return "left"
        elif shouldGoUp and self.canMoveInDirection(data, "up"):
          return "up"
        elif shouldGoDown and self.canMoveInDirection(data, "down"):
          return "down"
        return None

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

        print(data)

        move = None

        if self.shouldEat(data):
          print("GO EAT")
          move = self.getDirectionToGoToEat(data)

        print(f"current move: {move}")
        
        if move is None:
          move = random.choice(possible_moves)
          print("Random choice: ", move)
          for possible_move in possible_moves:
            # takes the first move it finds which won't go out of bounds or hit a snake
            if self.canMoveInDirection(data, possible_move):
              move = possible_move
              break

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
