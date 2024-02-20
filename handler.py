import json
import random
from logs.logger import logger
from typing import List, Optional
from providers.objects import Game, NightActions, DayActions, Player, Vote, Werewolf, Villager, Seer, Bodyguard, Witch

game: Optional[Game] = None

def play(event, context):
    global game 

    players = _init_players()
    game = Game(players)
    game.start()
    while not game.is_game_over():
        should_continue = _play_round(game)
        if not should_continue:
            break

    game.end()
    return _respond(game)

def _play_round(game: Game):
    night_actions: NightActions = game.new_night()
    # night moves
    # 1 -  werewolves kill a player
    logger.info("\nWerewolves vote to kill a player")
    night_actions.werewolf_victim = _collect_werewolf_votes().player
    # 2 - bodyguard saves a player
    night_actions.bodyguard_saved_player = _let_bodyguard_save()
    # 3 - seer investigates a player
    night_actions.did_seer_find_werewolf = _let_seer_investigate()
    # 4 - witch saves a player
    night_actions.did_witch_save_werewolf_victim = _let_witch_save()
    # 5 - witch kills a player
    night_actions.witch_victim = _let_witch_kill()

    game.process_night_actions(night_actions)

    day_actions: DayActions = game.new_day()
    game.announce_last_night_results()
    if game.is_game_over():
        return False
    
    # day moves
    # 1 - the village votes to kill a player
    logger.info("\nVillagers discuss and vote to kill a player")
    day_actions.village_victim = _collect_village_votes().player
    game.process_day_actions(day_actions)
    game.announce_todays_results()
    return True


def _respond(game):
    body = {
            "winners": [winner.toJson() for winner in game.winners],
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

def _collect_werewolf_votes(_villagers: List[Player] = [])->Vote:
    global game
    if game is None:
        raise ValueError("Game has not started yet.")

    game.start_new_werewolves_vote()

    if len(_villagers) == 0:
        villagers: List[Player] = game.get_villagers()
    else:
        villagers: List[Player] = _villagers

    werewolves: List[Player] = game.get_werewolves()
    for werewolf in werewolves:
        # pick a random villager
        victim = random.choice(villagers)
        game.add_werewolf_vote(werewolf_player=werewolf, victim_player=victim)

    logger.info(f"Current Votes {game.get_werewolves_votes()}")
    highest_votes = game.get_highest_werewolves_votes()
    if len(highest_votes) > 1:
        logger.info("There is a tie")
        logger.info("Werewolves need to vote again")
        tied_players = [vote.player for vote in highest_votes]
        return _collect_werewolf_votes(tied_players)
    else:
        # get the player with the highest votes
        highest_vote = highest_votes[0]
        logger.info(f"Werewolves have voted to kill {highest_vote.player}")
        game.end_werewolves_vote()
        return highest_vote

def _let_seer_investigate() -> bool:
    logger.info("")

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    seer = game.get_seer()
    if seer is None or not seer.is_alive:
        logger.info("Seer is dead. No investigation")
        return False
    
    players = [player for player in game.get_players_alive() if player != seer]
    investigated_player = random.choice(players)
    logger.info(f"Seer investigates {investigated_player}")
    is_werewolf = game.is_werewolf(investigated_player)
    return is_werewolf
       
def _let_bodyguard_save() -> Optional[Player]:
    logger.info("")

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    bodyguard = game.get_bodyguard()
    if bodyguard is None or not bodyguard.is_alive:
        logger.info("Bodyguard is dead. No saving")
        return None
    
    last_bodyguard_saved_player = game.get_last_bodyguard_saved_player()
    
    players = game.get_players_alive()
    saved_player = random.choice(players)
    if last_bodyguard_saved_player is not None and saved_player == last_bodyguard_saved_player:
        logger.info("Bodyguard can't save the same player twice in a row")
        return _let_bodyguard_save()
    
    logger.info(f"Bodyguard saves {saved_player}")
    return saved_player

def _let_witch_save() -> bool:
    logger.info("")

    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    witch = game.get_witch()
    if witch is None or not witch.is_alive:
        logger.info("Witch is dead. No saving")
        return False
    
    if game.is_witch_save_potion_used():
        logger.info("Witch has already used the save potion")
        return False
    
    options = [True, False]
    save_werewolf_victim = random.choice(options)
    if save_werewolf_victim:
        game.set_witch_save_potion_used()
    else:
        logger.info("Witch chose not to save the werewolf victim tonight.")

    return save_werewolf_victim

def _let_witch_kill() -> Optional[Player]:
    global game
    if game is None:
        raise ValueError("Game has not started yet.")
    
    witch = game.get_witch()
    if witch is None or not witch.is_alive:
        logger.info("Witch is dead. No killing")
        return None
    
    if game.is_witch_kill_potion_used():
        logger.info("Witch has already used the kill potion")
        return None
    
    options = [True, False]
    use_kill_potion = random.choice(options)
    if use_kill_potion:
        players = [player for player in game.get_players_alive() if player != witch]
        killed_player = random.choice(players)
        game.set_witch_kill_potion_used(killed_player)
        return killed_player
    else:
        logger.info("Witch chose not to kill a player tonight.")
        return None

def _collect_village_votes(_suspected_players: List[Player] = [])->Vote:
    global game
    if game is None:
        raise ValueError("Game has not started yet.")

    game.start_new_village_vote()
    players_alive = game.get_players_alive()

    if len(_suspected_players) == 0:
        suspected_players = players_alive
    else:
        suspected_players = _suspected_players

    suspected_villagers: List[Player] = [player for player in suspected_players if not game.is_werewolf(player)]

    for player in players_alive:
        if game.is_werewolf(player):
            victim = random.choice(suspected_villagers)
        else:
            victim = random.choice(suspected_players)
        game.add_village_vote(player, victim)

    logger.info(f"Current Votes {game.get_village_votes()}")
    highest_votes = game.get_highest_village_votes()
    if len(highest_votes) > 1:
        logger.info("There is a tie")
        logger.info("Everyone needs to vote again")
        tied_players = [vote.player for vote in highest_votes]
        return _collect_village_votes(tied_players)
    else:
        # get the player with the highest votes
        highest_vote = highest_votes[0]
        logger.info(f"The Village has voted to kill {highest_vote.player}")
        game.end_village_vote()
        return highest_vote
