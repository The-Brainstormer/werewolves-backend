import json
from typing import Optional
from providers.objects import Game, Player, Role, RoleAction, PlayerAction, Werewolf, Villager, Seer, Bodyguard, Witch

game: Optional[Game] = None

def start(event, context):
   # create 11 players. 4 werewolves, 1 seer, 1 bodyguard, 1 witch, 4 villagers
    player_1 = Player(1, 'John', Werewolf())
    player_2 = Player(2, 'Jane', Werewolf())
    player_3 = Player(3, 'Tom', Werewolf())
    player_4 = Player(4, 'Jerry', Werewolf())
    player_5 = Player(5, 'Sue', Seer())
    player_6 = Player(6, 'Mary', Villager())
    player_7 = Player(7, 'Harry', Villager())
    player_8 = Player(8, 'Larry', Villager())
    player_9 = Player(9, 'Carry', Villager())
    player_10 = Player(9, 'Andy', Bodyguard())
    player_11 = Player(10, 'Vikky', Witch())

    players = [player_1, player_2, player_3, player_4, player_5, player_6, player_7, player_8, player_9, player_10, player_11]

    global game 
    game = Game(players)
    game.start()
    game.next_night()
    # werewolves vote to kill players
    player_1.take_action(PlayerAction(RoleAction.Kill, player_6))
    player_2.take_action(PlayerAction(RoleAction.Kill, player_7))
    player_3.take_action(PlayerAction(RoleAction.Kill, player_5))
    player_4.take_action(PlayerAction(RoleAction.Kill, player_6))

    # seer investigates a player
    player_5.take_action(PlayerAction(RoleAction.Investigate, player_1))

    # bodyguard saves a player
    player_10.take_action(PlayerAction(RoleAction.Save, player_6))

    # witch saves a player
    player_11.take_action(PlayerAction(RoleAction.Save, player_9))

    # witch kills a player
    player_11.take_action(PlayerAction(RoleAction.Kill, player_7))

    game.next_day()

    body = {
        "message": "Welcome to the game of Werewolf!",
    }
    return {"statusCode": 200, "body": json.dumps(body)}


def end(event, context):
    if game is None:
        body = {
            "message": "Game has not started yet.",
        }
        return {"statusCode": 400, "body": json.dumps(body)}
    
    game.end()
    body = {
        "message": "Game over!",
    }
    return {"statusCode": 200, "body": json.dumps(body)}