import json
import random
from typing import List, Optional
from providers.objects import Game, NightResult, Player, Vote, Werewolf, Villager, Seer, Bodyguard, Witch

game: Optional[Game] = None

def play(event, context):
    global game 

    players = _init_players()
    game = Game(players)
    game.start()
    night_result: NightResult = game.new_night()

    # night moves
    # 1 -  werewolves kill a player
    night_result.werewolf_victim = _collect_werewolf_votes().player
    # we cant kill the player if they're saved by the bodyguard or witch
    # game.kill_player(werewolf_victim, "Killed by Werewolves")

    # 2 - bodyguard saves a player
    night_result.bodyguard_saved_player = _let_bodyguard_save()
    # 3 - seer investigates a player
    night_result.did_seer_find_werewolf = _let_seer_investigate()
    # 4 - witch saves a player
    night_result.did_witch_save_werewolf_victim = _let_witch_save()
    # 5 - witch kills a player
    night_result.witch_killed_player = _let_witch_kill()

    game.process_and_end_night(night_result)

    # game.next_day()
    

    game.end()
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
    print("\n")
    # todo, when there is a tie, werewolves need to vote again but only the ones who tied

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

    print(f"Current Votes", [vote for player, vote in game.werewolf_votes.items()])
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

def _let_seer_investigate() -> bool:
    print("\n")

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    seer = game.get_seer()
    if seer is None or not seer.is_alive:
        print("Seer is dead. No investigation")
        return False
    
    players = game.get_players_alive()
    investigated_player = random.choice(players)
    print("Seer investigates", investigated_player)
    is_werewolf = game.is_werewolf(investigated_player)
    if is_werewolf:
        print(f"{investigated_player} is a werewolf")
        return True
    else:
        print(f"{investigated_player} is not a werewolf")
        return False
    
def _let_bodyguard_save() -> Optional[Player]:
    print("\n")

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    bodyguard = game.get_bodyguard()
    if bodyguard is None or not bodyguard.is_alive:
        print("Bodyguard is dead. No saving")
        return None
    
    last_bodyguard_saved_player = game.get_last_bodyguard_saved_player()
    
    players = game.get_players_alive()
    saved_player = random.choice(players)
    if last_bodyguard_saved_player is not None and saved_player == last_bodyguard_saved_player:
        print("Bodyguard can't save the same player twice in a row")
        return _let_bodyguard_save()
    
    print("Bodyguard saves", saved_player)
    return saved_player

def _let_witch_save() -> bool:
    print("\n")

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    witch = game.get_witch()
    if witch is None or not witch.is_alive:
        print("Witch is dead. No saving")
        return False
    
    if game.is_witch_save_potion_used():
        print("Witch has already used the save potion")
        return False
    
    options = [True, False]
    save_werewolf_victim = random.choice(options)
    if save_werewolf_victim:
        game.set_witch_save_potion_used()

    return save_werewolf_victim

def _let_witch_kill() -> Optional[Player]:
    print("\n")
    # todo - cant kill the same player you're saving

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    witch = game.get_witch()
    if witch is None or not witch.is_alive:
        print("Witch is dead. No killing")
        return None
    
    if game.is_witch_kill_potion_used():
        print("Witch has already used the kill potion")
        return None
    
    players = game.get_players_alive()
    killed_player = random.choice(players)
    game.set_witch_kill_potion_used(killed_player)
    return killed_player
