import sys
import csv
import copy

TEAM_REQUIREMENTS = ["PG", "SG", "SF", "PF", "C", "G", "F", "Util"]
SALARY_REQUIREMENT = 50000
MINIMUM_SALARY = 3000

POSITIONS = {
    'PG': ('PG', 'G', 'Util'),
    'SG': ('SG', 'G', 'Util'),
    'SF': ('SF', 'F', 'Util'),
    'PF': ('PF', 'F', 'Util'),
    'C':  ('C', 'Util')
}

class Player:
    def __init__(self, id, attrs):
        self.id = id
        self.position = attrs[0]
        self.name = attrs[1]
        self.cost = int(attrs[2])
        self.game = attrs[3]
        self.avgfp = float(attrs[4])

        self.value = self.cost/self.avgfp
        self.score = self.value * self.avgfp


    def positions(self):
        return POSITIONS[self.position]

class Team:
    def __init__(self):
        self.players = []
        self.player_ids = {}
        self.remaining_positions = copy.copy(TEAM_REQUIREMENTS)
        self.remaining_salary = copy.copy(SALARY_REQUIREMENT)

    def is_complete(self):
        len(self.remaining_positions) == 0

    def is_valid(self):
        if self.is_complete() and self.remaining_salary < 0:
            return False
        elif len(self.remaining_positions) == 0:
            return False
        elif not self.is_complete() and self.remaining_salary/len(self.remaining_positions) < MINIMUM_SALARY:
            return False
        else:
            return True


    def add(self, player):

        if(player.cost > self.remaining_salary): return False
        if(player.id in self.player_ids): return False

        pos = False
        for p in player.positions():
            if p in self.remaining_positions:
                self.remaining_positions.remove(p)
                pos = p
                break

        if pos:
            self.players.append(player)
            self.player_ids[player.id] = True
            self.remaining_salary = self.remaining_salary - player.cost

            if len(self.remaining_positions) > 0 and self.remaining_salary/len(self.remaining_positions) < MINIMUM_SALARY: return False

        return pos

    def avgfp(self):
        return sum([p.avgfp for p in self.players])

    def __str__(self):
        r = [p.name for p in self.players]
        r.append(str(self.avgfp()))
        return ", ".join(r)


    def copy(self):
        t = Team()
        t.players = copy.copy(self.players)
        t.player_ids = copy.copy(self.player_ids)
        t.remaining_positions = copy.copy(self.remaining_positions)
        t.remaining_salary = copy.copy(self.remaining_salary)
        return t

def load_players(csv_filename):
    print "Processing %s" % csv_filename

    players = []
    with open('dailies/' + csv_filename, 'rb') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx != 0:
                players.append(Player(idx, row))

    return players

def recommend_teams(players):
    valid_teams = []
    players.sort(key=lambda x: x.value, reverse=False)

    for p in players:
        t = Team()
        t.add(p)
        recurse_players(valid_teams, players, t)

    print "# of valid teams: %d" % len(valid_teams)

def recurse_players(valid_teams, players, team, count=1):
    if team.is_complete() and team.is_valid():
        valid_teams.append(team)
        print "Added valid team:"
        print team
    elif count > len(TEAM_REQUIREMENTS):
        del team
        sys.stdout.write('.')
    else:
        for p in players:
            t = team.copy()
            if t.add(p): recurse_players(valid_teams, players, t, count + 1)
            else:
                del t
                sys.stdout.write('.')

def run_tests():
    players = load_players("test.csv")
    recommend_teams(players)

def print_values(players):
    players.sort(key=lambda x: x.value)

    for p in players:
        print "%s\t%s\t%s\t%s" % (p.name, p.value, p.cost, p.avgfp)

if __name__ == "__main__":

    if(len(sys.argv) == 3):
        filename = sys.argv[2]
        action = sys.argv[1]
    elif(len(sys.argv) == 2):
        action = sys.argv[1]
        filename = None

    if filename: players = load_players(filename)

    if action == 'recommend':
        recommend_teams(players)
    elif action == 'values':
        print_values(players)
    elif action == 'test':
        run_tests()
