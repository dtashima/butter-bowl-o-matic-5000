import collections
from decimal import Decimal
import itertools

class ComparableMixin(object):
  def __eq__(self, other):
    return not self<other and not other<self
  def __ne__(self, other):
    return self<other or other<self
  def __gt__(self, other):
    return other<self
  def __ge__(self, other):
    return not self<other
  def __le__(self, other):
    return not other<self

class Record(ComparableMixin):
    LOOKUP = {}
    
    @staticmethod
    def get(wins, losses, ties):
        r = Record.LOOKUP.get((wins, losses, ties))
        if not r:
            r = Record(wins=wins, losses=losses, ties=ties)
            Record.LOOKUP[(wins, losses, ties)] = r
        return r

    def __init__(self, wins=0, losses=0, ties=0):
        self.wins = wins
        self.losses = losses
        self.ties = ties

    def __str__(self):
        return '({0}-{1}-{2})'.format(self.wins, self.losses, self.ties)

    def __repr__(self):
        return str(self)

#    def win(self):
#        self.wins += 1

#    def lose(self):
#        self.losses += 1

#    def tie(self):
#        self.ties += 1

    def __lt__(self, other):
        if self.wins != other.wins:
            res = self.wins < other.wins
        elif self.ties != other.ties:
            res = self.ties < other.ties
        else:
            res = self.losses > other.losses
        return res

def handleWinLose(record, oppRecord, wlt):
    if wlt > 0:
        return (Record.get(record.wins + 1, record.losses, record.ties),
                Record.get(oppRecord.wins, oppRecord.losses+1, oppRecord.ties))
#        record.win()
#        oppRecord.lose()
    elif wlt == 0:
        return (Record.get(record.wins, record.losses, record.ties + 1),
                Record.get(oppRecord.wins, oppRecord.losses, oppRecord.ties + 1))
#        record.tie()
#        oppRecord.tie()
    else:
        return (Record.get(record.wins, record.losses + 1, record.ties),
                Record.get(oppRecord.wins + 1, oppRecord.losses, oppRecord.ties))
#        record.lose()
#        oppRecord.win()

class Team(ComparableMixin):
    usePoints = False
    showMatches = False
    def __init__(self, name, division, pointsFor=0):
        self.name = name
        self.matches = []
        self.record = Record(0,0,0)
        self.divRecord = Record(0,0,0)
        self.h2h = collections.defaultdict(Record)
        self.pointsFor = pointsFor
        self.division = division

    def __str__(self):
        s = '{0} ({1}): Record: {2}; Division Record: {3};\n H2H: {4}; Points For: {5}\n' \
            .format(self.name, self.division, self.record, self.divRecord, self.h2h, self.pointsFor)
        if Team.showMatches:
            s += str(self.matches)
        return s

    def __repr__(self):
        return self.__str__()

    def plays(self, opponent, score, oppScore):
        self.matches.append((opponent.name, score, oppScore))
        if not isinstance(score, Decimal):
            score = Decimal(score)
        if not isinstance(oppScore, Decimal):
            oppScore = Decimal(oppScore)

        wlt = score.compare(oppScore)
        (self.record, opponent.record) = handleWinLose(self.record, opponent.record, wlt)

        if self.division == opponent.division:
            (self.divRecord, opponent.divRecord) = handleWinLose(self.divRecord, opponent.divRecord, wlt)

        (self.h2h[opponent.name], opponent.h2h[self.name]) = \
            handleWinLose(self.h2h[opponent.name], opponent.h2h[self.name], wlt)

        self.pointsFor += score
        opponent.pointsFor += oppScore

    def __lt__(self, other):
        if self.record != other.record:
            res = self.record < other.record
        elif self.divRecord != other.divRecord:
            res = self.divRecord < other.divRecord
        elif self.h2h[other.name] != other.h2h[self.name]:
            res = self.h2h[other.name] < other.h2h[self.name]
        elif Team.usePoints and self.pointsFor != other.pointsFor:
            res = self.pointsFor < other.pointsFor
        else:
            res = False # tie
        return res

class League(object):
    def __init__(self, teams=None):
        self.teams = {} # division -> list of teams
        self.teamLookup = {} # team name -> team
        if teams:
            for t in teams:
                self.addTeam(t)

    def addTeam(self, team):
        self.teamLookup[team.name] = team

        div = team.division
        divList = self.teams.get(div)
        if not divList:
            divList = []
            self.teams[div] = divList
        divList.append(team)
        divList.sort()

    def getTeam(self, teamName):
        return self.teamLookup.get(teamName)

    def teamList(self):
        return itertools.chain(*self.teams.values())

    def divisionWinners(self):
        for divList in self.teams.values():
            divList.sort()
        winners = {}
        for (division, teams) in self.teams.iteritems():
            top = topTeams(teams)
            if len(top) > 1:
                Team.showMatches  = True
                print 'Alert, Tie in Division winners: ' + str(top)
                Team.showMatches  = False
            winners[division] = top

        return winners

    def wildcardTeams(self, num):
        teams = []
        for divTeams in self.teams.values():
            for t in divTeams[0:len(divTeams)-1]:
                teams.append(t)

        res =  topTeams(teams, n=num)
        if len(res) > num:
            Team.showMatches  = True
            print 'Alert, Tie in wc teams: ' + str(res)
            Team.showMatches  = False
        return res

    def calculatePlayoffTeams(self):
        return (self.divisionWinners(), self.wildcardTeams(3))
        
def topTeams(teams, n=1):
    teams = list(teams)
    teams.sort(reverse=True)
    res = []
    for (i, t) in enumerate(teams):
        if i < n or (res and res[-1] == t):
            res.append(t)

    return res

