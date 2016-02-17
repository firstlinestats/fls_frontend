
import constants


def get_player_type(given):
    for option in constants.playerTypes:
        if option[1] == given:
            return option[0]
    return 0


def init_player():
    numberkeys = ["g", "a1", "a2", "p", "cf", "ca", "ff", "fa", "g+-", "fo_w", "fo_l",
    "hit+", "hit-", "pn+", "pn-", "gf", "ga", "sf", "sa", "msf", "msa", "bsf", "bsa"]
    strkeys = ["name", "position", "team"]
    player = {}
    for n in numberkeys:
        player[n] = 0
    for n in strkeys:
        player[n] = ""
    return player
