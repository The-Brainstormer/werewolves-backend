import json
import random
from typing import Dict, List, Optional
from providers.objects import Game, Player, Vote, Werewolf, Villager, Seer, Bodyguard, Witch

game: Optional[Game] = None

def start(event, context):
    global game 

    players = _init_players()
    game = Game(players)
    game.start()
    game.next_night()

    # night moves
    # 1 -  werewolves kill a player
    highest_vote = _collect_werewolf_votes()
    victim = highest_vote.player
    game.kill_player(victim, "Killed by Werewolves")


    # # seer investigates a player
    # player_5.take_action(PlayerAction(RoleAction.Investigate, player_1))

    # # bodyguard saves a player
    # player_10.take_action(PlayerAction(RoleAction.
    # Save, player_6))

    # # witch saves a player
    # player_11.take_action(PlayerAction(RoleAction.Save, player_9))

    # # witch kills a player
    # player_11.take_action(PlayerAction(RoleAction.Kill, player_7))

    # game.next_day()
    

    body = {
        "winners": game.winners,
        "winner_role": game.winner_role,
    }
    return {"statusCode": 200, "body": json.dumps(body)}


def _init_players()->List[Player]:
    # create 11 players. 4 werewolves, 1 seer, 1 bodyguard, 1 witch, 4 villagers
    player_1 = Player(1, 'John', Werewolf())
    player_2 = Player(2, 'Jane', Werewolf())
    player_3 = Player(3, 'Tom', Werewolf())
    player_4 = Player(4, 'Jerry', Werewolf())
    player_5 = Player(5, 'Sue', Seer())
    player_6 = Player(6, 'Mary', Villager())
    player_7 = Player(7, 'Harry', Villager())
    player_8 = Player(8, 'Larry', Villager())
    player_9 = Player(9, 'Henry', Villager())
    player_10 = Player(10, 'Andy', Bodyguard())
    player_11 = Player(11, 'Vikky', Witch())

    players = [player_1, player_2, player_3, player_4, player_5, player_6, player_7, player_8, player_9, player_10, player_11]
    return players


def _collect_werewolf_votes()->Vote:
    global game
    if game is None:
        raise ValueError("Game has not started yet.")

    game.start_new_werewolves_vote()

    villagers: List[Player] = game.get_villagers()
    werewolves: List[Player] = game.get_werewolves()
    for werewolf in werewolves:
        # pick a random villager
        victim = random.choice(villagers)
        game.add_werewolf_vote(werewolf_player=werewolf, victim_player=victim)

    print(f"Current Votes", game.werewolf_votes)
    highest_votes = game.get_highest_werewolves_votes()
    if len(highest_votes) > 1:
        print("There is a tie")
        print("Werewolves need to vote again")
        return _collect_werewolf_votes()
    else:
        # get the player with the highest votes
        highest_vote = highest_votes[0]
        print("Werewolves have voted to kill", highest_vote.player)
        game.end_werewolves_vote()
        return highest_vote


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