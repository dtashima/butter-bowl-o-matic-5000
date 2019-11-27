import collections
import copy
import itertools
import re

from buttercup.timer import Timer
from buttercup.team import Team, League

def load_teams(path):
    teams = []
    with open(path, 'r') as f:
        teams = f.read().strip().split('\n')
    teams = [t.split(',') for t in teams]
    teams = [Team(t[0], t[1]) for t in teams]
    return teams

def load_scores(league, path):
    teamlookup = dict([(t.name, t) for t in league.teamList()])

    with open(path, 'r') as f:
        doc = f.readlines()
        
    if doc is None:
        return
    
    section = None
    
    for line in doc:
        line = line.strip()
        if not line:
            continue
        if section == 'scores':
            m =  re.match('([^(]+)\W+\([WL]\)\W*([^(]+)\W+\([WL]\)\W+([0-9.]+) - ([0-9.]+)\W*', line)
            if not m:
                section = 'standings'
                continue
            teamName1 = m.group(1)
            teamName2 = m.group(2)
            score1 = m.group(3)
            score2 = m.group(4)

            team1 = teamlookup[teamName1]
            team2 = teamlookup[teamName2]
            team1.plays(team2, score1, score2)
            continue

        if line.startswith('PERIOD'):
            section = 'scores'
            continue

    return league

def load_schedule(path):
    schedule = []
    with open(path, 'r') as f:
        doc = f.readlines()
    week = None
    for line in doc:
        if line.startswith('PERIOD'):
            if week:
                schedule.append(week)
            week = []
            continue
        items = line.split('\t')
        week.append((items[0], items[1]))
    schedule.append(week)
    return schedule

class PlayoffCalculator(object):
    def __init__(self, league):
        self.league = league

    def calculateWinners(self, results):
        teamNames = [t.name for t in self.league.teamList()]
        eliminated = set(teamNames)
        clinchedPlayoffs = set(teamNames)
        clinchedDiv = set(teamNames)
        divWinnerCount = collections.defaultdict(int)
        madePlayoffsCount = collections.defaultdict(int)

        for (i,res) in enumerate(results):
            (divWinners, wcWinners) = res.calculatePlayoffTeams()
            divNames = set([t.name for ts in divWinners.values() for t in ts])
            wcNames = set([t.name for t in wcWinners])
            for t in itertools.chain(*divWinners.values()):
                eliminated.discard(t.name)
            for t in wcWinners:
                eliminated.discard(t.name)
            winners = wcNames | divNames
            clinchedPlayoffs &= winners
            clinchedDiv &= divNames

            for n in divNames:
                divWinnerCount[n] += 1
                madePlayoffsCount[n] += 1

            for n in wcNames:
                madePlayoffsCount[n] += 1


        return (clinchedDiv, clinchedPlayoffs, eliminated, divWinnerCount, madePlayoffsCount)

    def playmatches(self, schedule):
        results = [] # all possible league combinations after playing out schedule
        
        q = [] # a queue
        q.append((self.league, 0, 0)) # league, week, match
        step = 0
        while q:
            step += 1
            (league, weeknum, matchnum) = q.pop(0)
            print 'at step {0}, week: {1}, match: {2}'.format(step, weeknum, matchnum)
            (team1, team2) = schedule[weeknum][matchnum]
            if matchnum < len(schedule[weeknum])-1:
                matchnum += 1
            else:
                matchnum = 0
                weeknum +=1
                    
            for (winner, loser) in ((team1, team2), (team2, team1)):
                ltemp = copy.deepcopy(league)
                t1 = ltemp.getTeam(winner)
                t2 = ltemp.getTeam(loser)
                t1.plays(t2, 0.001,0)
                if weeknum == len(schedule) and matchnum == 0:
                    # done
                    results.append(ltemp)
                else:
                    q.append((ltemp, weeknum, matchnum))
        return results
            

def main():
    import itertools
    teams = load_teams('/Users/tash/projects/buttercup/teams.txt')
    league = League(teams)
    
    league = load_scores(league, '/Users/tash/projects/buttercup/scores.txt')
    schedule = load_schedule('/Users/tash/projects/buttercup/schedule.txt')
    print schedule

    with Timer('playoff calculator'):
        pc = PlayoffCalculator(league)
        res = pc.playmatches(schedule)
        (div, cl, elim, divCount, playoffsCount) = pc.calculateWinners(res)
        print (div, cl, elim)
        print 'division Count: ' + str(divCount)
        print 'playoff count: ' + str(playoffsCount)
    
    
main()
    
