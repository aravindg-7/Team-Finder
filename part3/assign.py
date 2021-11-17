#!/usr/local/bin/python3
# assign.py : Assign people to teams
#
# Code by: Aravind Ganta aganta
#
# Based on skeleton code by D. Crandall and B551 Staff, September 2021
#

import sys

def get_rawdata(txt):
    with open(txt, "r") as f:
        return [[s for s in line.split()] for line in f]


def student_pref(txt):
    raw_data = get_rawdata(txt)
    preferences = {}
    for i in raw_data:
        preferences[i[0]] = []
        preferences[i[0]].append(i[1])
        preferences[i[0]].append(i[2])
    return preferences


def get_students(txt):
    data = get_rawdata(txt)
    list = []
    for i in data:
        list.append(i[0])
    return list


def get_requests(name, student_pref):
    l = student_pref[name][0]
    l = l.split('-')
    l.remove(name)
    while ('xxx' in l):
        l.remove('xxx')
    while ('zzz' in l):
        l.remove('zzz')
    return l


def get_req_team_size(name, student_pref):
    l = student_pref[name][0]
    l = l.split('-')
    return len(l)


def get_exceptions(name, student_pref):
    l = student_pref[name][1]
    l = l.split(',')
    if '_' in l:
        l.remove('_')
    return l


def get_cost(teams, preferences):
    cost = 0
    for team in teams:
        cost += 5
        team_it = team.split('-')
        for s in team_it:
            if (get_req_team_size(s, preferences) != len(team_it)):
                cost += 2
            frnds = get_requests(s, preferences)
            foes = get_exceptions(s, preferences)
            for f in foes:
                if f in team_it:
                    cost += 10
            for f in frnds:
                if f not in team_it:
                    cost += 3
    return cost


def update_teams(name1, name2, teamlist):
    lst = teamlist.copy()
    index = lst.index(name1)
    team1 = name1.split('-')
    team2 = name2.split('-')
    if (len(team1) + len(team2) <= 3):
        if name1<name2:
            new_name = name1 + '-' + name2
        else:
            new_name = name2 + '-' + name1
    lst[index] = new_name
    lst.remove(name2)
    return lst


def successor(teamlist, team):
    list = []
    team_it = team.split('-')
    for i in teamlist:
        it = i.split('-')
        if len(team_it) + len(it) <= 3 and team != i:
            list.append(i)

    return list


def check_converse(team, succ, temp, preferences,temp_subopt):
    slist = successor(temp,succ)
    old_cost = get_cost(temp,preferences)
    if slist:
        best,cost = best_succ(slist,succ,temp,preferences,old_cost,temp_subopt)
        if best:
            if best == team:
                temp = update_teams(team, succ, temp)
            else:
                sub_opt_add(temp_subopt, update_teams(team, succ, temp))
                temp = update_teams(best, succ, temp)
    return temp



def best_succ(slist,team,temp,preferences,cost,temp_subopt):
    best_succ = ""
    for succ in slist:
        tlist = update_teams(team, succ, temp)
        new_cost = get_cost(tlist, preferences)
        if new_cost < cost:
            cost = new_cost
            best_succ =succ
        else:
            sub_opt_add(temp_subopt, tlist)


    return best_succ,cost

def sub_opt_add(temp_subopt,teams):

    tmplistcpy = temp_subopt.copy()
    tmcpy = teams.copy()
    if tmcpy not in tmplistcpy:
        for lst in tmplistcpy:
            lst.sort()
        tmcpy.sort()
        if tmcpy in tmplistcpy:
            pass
        else:
            temp_subopt.append(teams)



def best_team(temp, preferences, team, cost,temp_subopt):
    slist = successor(temp, team)

    if slist:
        succ,new_cost = best_succ(slist,team,temp,preferences,cost,temp_subopt)
        if succ:
            temp = check_converse(team, succ, temp, preferences,temp_subopt)

    return temp


def solver(input_file):
    """
    1. This function should take the name of a .txt input file in the format indicated in the assignment.
    2. It should return a dictionary with the following keys:
        - "assigned-groups" : a list of groups assigned by the program, each consisting of usernames separated by hyphens
        - "total-cost" : total cost (time spent by instructors in minutes) in the group assignment
    3. Do not add any extra parameters to the solver() function, or it will break our grading and testing code.
    4. Please do not use any global variables, as it may cause the testing code to fail.
    5. To handle the fact that some problems may take longer than others, and you don't know ahead of time how
       much time it will take to find the best solution, you can compute a series of solutions and then
       call "yield" to return that preliminary solution. Your program can continue yielding multiple times;
       our test program will take the last answer you 'yielded' once time expired.
    """

    """"
    # Simple example. First we yield a quick solution
    yield ({"assigned-groups": ["vibvats-djcran-zkachwal", "shah12", "vrmath"],
            "total-cost": 12})

    # Then we think a while and return another solution:
    time.sleep(10)
    yield ({"assigned-groups": ["vibvats-djcran-zkachwal", "shah12-vrmath"],
            "total-cost": 10})

    # This solution will never befound, but that's ok; program will be killed eventually by the
    #  test script.
    while True:
        pass

    yield ({"assigned-groups": ["vibvats-djcran", "zkachwal-shah12-vrmath"],
            "total-cost": 9})
    """
    preferences = student_pref(input_file)
    students = get_students(input_file)
    teams = []
    sub_optimal = []
    for s in students:
        teams.append(s)
    cost = get_cost(teams, preferences)

    yield ({"assigned-groups": teams,
            "total-cost": cost})
    temp = teams.copy()
    length = len(temp) - 1
    cost = get_cost(temp, preferences)
    while (length):
        lst = best_team(temp, preferences, temp[length], cost,sub_optimal)

        temp = lst

        cost = get_cost(temp, preferences)
        length -= 1
    yield ({"assigned-groups": temp,
            "total-cost": cost})

    while (sub_optimal):
        for templist in sub_optimal:
            for team in templist:
                lst = best_team(templist, preferences, team, cost,sub_optimal)
                new_cost = get_cost(lst,preferences)
                if new_cost< cost:
                    cost = new_cost
                    yield ({"assigned-groups": lst,
                            "total-cost": new_cost})
            sub_optimal.remove(templist)



if __name__ == "__main__":
    if (len(sys.argv) != 2):
        raise (Exception("Error: expected an input filename"))

    for result in solver(sys.argv[1]):
        print("----- Latest solution:\n" + "\n".join(result["assigned-groups"]))
        print("\nAssignment cost: %d \n" % result["total-cost"])
