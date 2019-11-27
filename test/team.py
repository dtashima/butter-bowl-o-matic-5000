from decimal import Decimal
import unittest

from buttercup.team import Team, Record, League, handleWinLose, topTeams

class Test(unittest.TestCase):
    def testRecord(self):
        rec1 = Record(5,2,1)
        rec2 = Record(6,2,1)
        self.assertTrue(rec1 < rec2)

        rec1 = Record(5,2,1)
        rec2 = Record(5,2,2)
        self.assertTrue(rec2 > rec1)

        rec1 = Record(5,2,1)
        rec2 = Record(5,2,1)
        self.assertEqual(rec1, rec2)

    def testTeam(self):
        a1team = Team('a1', 'div1')
        b1team = Team('b1', 'div1')
        c1team = Team('c1', 'div1')
        a2team = Team('a2', 'div2')
        b2team = Team('b2', 'div2')
        c2team = Team('c2', 'div2')
        a1team.plays(b1team, '100', '50')
        print
        print 'testing overall record'
        print a1team
        print b1team
        # test overall record
        self.assertTrue(a1team > b1team)

        # test division record
        a1team.plays(a2team, '50', '150')
        b1team.plays(b2team, '100', '50')
        
        print
        print 'testing div record'
        print a1team
        print b1team
        self.assertTrue(a1team > b1team)

        # test h2h
        a1team.plays(c1team, '50', '100')
        b1team.plays(c1team, '100', '50')
        a1team.plays(c2team, '100', '50')
        b1team.plays(c2team, '50', '100')

        print
        print 'testing h2h'
        print a1team
        print b1team
        self.assertTrue(a1team > b1team)

        # test points for
        a1team.plays(b1team, '50', '100')
        a1team.plays(c1team, '1000', '100')
        b1team.plays(c1team, '50', '100')

        print
        print 'testing points for'
        print a1team
        print b1team
        Team.usePoints = False
        self.assertTrue(a1team == b1team)
        Team.usePoints = True
        self.assertTrue(a1team > b1team)

        
    def testWinners(self):
        a1team = Team('a1', 'div1')
        b1team = Team('b1', 'div1')
        c1team = Team('c1', 'div1')
        d1team = Team('d1', 'div1')
        a2team = Team('a2', 'div2')
        b2team = Team('b2', 'div2')
        c2team = Team('c2', 'div2')
        d2team = Team('d2', 'div2')

        league = League()
        for t in [a1team, b1team, c1team, d1team, a2team, b2team, c2team, d2team]:
            league.addTeam(t)

        a1team.plays(b1team, '100', '50')
        a1team.plays(c1team, '100', '50')
        a1team.plays(d1team, '100', '50')

        b1team.plays(c1team, '102', '50')
        b1team.plays(d1team, '100', '50')
        
        c1team.plays(d1team, '101', '50')

        a2team.plays(b2team, '100', '50')
        a2team.plays(c2team, '100', '50')
        a2team.plays(d2team, '100', '50')

        b2team.plays(c2team, '100', '50')
        b2team.plays(d2team, '100', '50')
        
        c2team.plays(d2team, '100', '50')

        divWinners = league.divisionWinners()
        print 'division winners: ' + str(divWinners)
        self.assertEqual(divWinners['div1'], [a1team])
        self.assertEqual(divWinners['div2'], [a2team])
        
        wc = league.wildcardTeams(3)
        print 'Wildcard teams: ' + str(wc)
        self.assertEqual(len(wc), 3)
        self.assertEqual(wc[0], b1team)
        self.assertEqual(wc[1], b2team)
        self.assertEqual(wc[2], c1team)

    def test_topTeams(self):
        teams = [100, 100, 50, 25]
        self.assertEqual(topTeams(teams), [100, 100])

        teams = [100, 75, 50, 50, 50, 25, 15]
        self.assertEqual(topTeams(teams, n=3), [100, 75, 50, 50, 50])

if __name__ == '__main__':
    unittest.main()

    
