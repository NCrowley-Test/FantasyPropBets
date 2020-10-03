from bs4 import BeautifulSoup
import requests
import json

def get_Player_Names(rush_yards,pass_yards,receiving_yards):
    player_Names = []
    for i in range(len(rush_yards)):
        if rush_yards[i][0] not in player_Names:
            player_Names.append(rush_yards[i][0])

    for i in range(len(pass_yards)):
        if pass_yards[i][0] not in player_Names:
            player_Names.append(pass_yards[i][0])

    for i in range(len(receiving_yards)):
        if receiving_yards[i][0] not in player_Names:
            player_Names.append(receiving_yards[i][0])
    player_Names.sort()
    return player_Names
def scaling_factor(prop_stat,vig):
    #Stats are given with a vig and betting odds, so we need to adjust the stat based on what is actually happening
    if vig < 0:
        scaling_factor = 2 * ((abs(vig) / (abs(vig) + 100))-.0283)
        result = prop_stat * scaling_factor
    # Sometimes vig is positive, so we need to convert to negative vig and then scale again
    else:
        scaling_factor = 2 * ((100 / (abs(vig) + 100)) - .0283)
        result = prop_stat * scaling_factor
    if result < 0:
        result = 0
    return result
def get_qb_props():
    py_url="https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory=passing-yards"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    page = requests.get(py_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    #Get the QB passing Yards page

    player_Name = []
    passing_Yards = []
    passing_TDS = []

    for players in soup.find_all(class_='sportsbook-event-accordion__children-wrapper'):
        player1 = players.find(class_="sportsbook-participant-name")
        temp_p1 = player1.contents[0]
        player2 = player1.find_next(class_="sportsbook-participant-name")
        temp_p2 = player2.contents[0]
        passing_Yards_Player_1 = players.find(class_="sportsbook-outcome-cell__label")
        passing_Yards.append([temp_p1,passing_Yards_Player_1.contents[0][5:]])
        passing_Yards_Player_2 = passing_Yards_Player_1.find_next(class_="sportsbook-outcome-cell__label")
        passing_Yards.append([temp_p2,passing_Yards_Player_2.contents[0][5:]])
        #Players come in pairs due to how draftkings does things, grab both names and passing yards

    py_url = "https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory=td-passes"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    page = requests.get(py_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    for players in soup.find_all(class_='sportsbook-event-accordion__wrapper expanded'):
        #Changed URL to get passing TDs, then getting those.
        player1_Name = players.find(class_="sportsbook-participant-name").contents[0]
        player2_Name = player1_Name.find_next(class_="sportsbook-participant-name").contents[0]
        passing_TDS_Player_1 = players.find(class_="sportsbook-outcome-cell")
        temp_Passing_TDs_1 = str(passing_TDS_Player_1.contents[0])
        x = float(temp_Passing_TDs_1[22:25])
        string_vig_player_1 = players.find(class_="sportsbook-odds american default-color").contents[0]
        vig_player_1 = float(string_vig_player_1)
        passing_TDS_Player_2 = passing_TDS_Player_1.find_next(class_="sportsbook-outcome-cell")
        temp_Passing_TDs_2 = str(passing_TDS_Player_2.contents[0])
        y = float(temp_Passing_TDs_2[22:25])
        vig_player_2 = float(string_vig_player_1.find_next(class_="sportsbook-odds american default-color").contents[0])

        x = scaling_factor(x,vig_player_1)
        y = scaling_factor(y, vig_player_2)
        passing_TDS.append([player1_Name,x])
        passing_TDS.append([player2_Name,y])
        #Need to apply vig to passing TDs



    return passing_Yards,passing_TDS

def get_rushing_yards():
    py_url = "https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory=rushing-yards"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    page = requests.get(py_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    tag_Name = "sportsbook-participant-name"
    tag_Over_Yards = "sportsbook-outcome-cell__label"
    tag_Vig = "sportsbook-odds american default-color"
    num_Players = len(soup.find_all(class_=tag_Name))
    prop_Rush_Yards = []
    over_Rec = []
    for i in range(len(soup.find_all(class_=tag_Over_Yards))):
        if str(soup.find_all(class_=tag_Over_Yards)[i].contents[0])[0] == "O":
            over_Rec.append(str(soup.find_all(class_=tag_Over_Yards)[i].contents[0])[5:])
    for i in range(num_Players):
        cur_Player_Name = soup.find_all(class_=tag_Name)[i].contents[0]
        cur_Over_Yards =  float(over_Rec[i])
        cur_Vig = float(soup.find_all(class_=tag_Vig)[i].contents[0])
        adj_Yards = scaling_factor(cur_Over_Yards,cur_Vig)

        prop_Rush_Yards.append([cur_Player_Name,adj_Yards])
    return prop_Rush_Yards


def get_receiving_yards():
    py_url = "https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory=receiving-yards"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    page = requests.get(py_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    tag_Name = "sportsbook-participant-name"
    tag_Over_Yards = "sportsbook-outcome-cell__label"
    tag_Vig = "sportsbook-odds american default-color"
    num_Players = len(soup.find_all(class_=tag_Name))
    prop_Receiving_Yards = []

    over_Rec = []

    for i in range(len(soup.find_all(class_=tag_Over_Yards))):
        if str(soup.find_all(class_=tag_Over_Yards)[i].contents[0])[0] == "O":
            over_Rec.append(str(soup.find_all(class_=tag_Over_Yards)[i].contents[0])[5:])
    for i in range(num_Players):
        cur_Player_Name = soup.find_all(class_=tag_Name)[i].contents[0]
        cur_Over_Yards = float(over_Rec[i])
        cur_Vig = float(soup.find_all(class_=tag_Vig)[i*2].contents[0])
        adj_Yards = scaling_factor(cur_Over_Yards, cur_Vig)

        prop_Receiving_Yards.append([cur_Player_Name, adj_Yards])
    return prop_Receiving_Yards

def get_receptions():
    py_url = "https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory=receptions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    page = requests.get(py_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    tag_Name = "sportsbook-participant-name"
    tag_Rec = "sportsbook-outcome-cell__label"
    tag_Vig = "sportsbook-odds american default-color"
    num_Players = len(soup.find_all(class_=tag_Name))
    prop_Receptions = []
    over_Rec = []

    for i in range(len(soup.find_all(class_=tag_Rec))):
        if str(soup.find_all(class_=tag_Rec)[i].contents[0])[0] == "O":
            over_Rec.append(str(soup.find_all(class_=tag_Rec)[i].contents[0])[5:])
    for i in range(num_Players):
        cur_Player_Name = soup.find_all(class_=tag_Name)[i].contents[0]
        cur_Over_Rec = float(over_Rec[i])
        cur_Vig = float(soup.find_all(class_=tag_Vig)[i*2].contents[0])
        adj_Rec = scaling_factor(cur_Over_Rec, cur_Vig)

        prop_Receptions.append([cur_Player_Name, adj_Rec])
    return prop_Receptions

def get_non_pass_TD():
    py_url = "https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory=touchdown-scorer"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    page = requests.get(py_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    tag_Name = "scorer-7__player"
    tag_Odds_To_Score = "sportsbook-odds american default-color"
    #So they show 3 different odds, we only care about the third column
    #couldn't just be the first one, noooooo
    num_Players = len(soup.find_all(class_=tag_Name))
    prop_Non_Pass_TD = []
    for i in range(num_Players):
        cur_Player_Name = soup.find_all(class_=tag_Name)[i].contents[0]
        temp_Cur_Name = str(cur_Player_Name)
        if temp_Cur_Name[:5] != "Any O":
            cur_Vig = float(soup.find_all(class_=tag_Odds_To_Score)[i*3+2].contents[0])
            prop_Non_Pass_TD.append([cur_Player_Name,scaling_factor(.5,cur_Vig)])

    return prop_Non_Pass_TD



def create_CSV():
    pass_yards, pass_TDs = get_qb_props()
    rush_yards = get_rushing_yards()
    receiving_yards = get_receiving_yards()
    receptions = get_receptions()
    player_Names = get_Player_Names(rush_yards, pass_yards, receiving_yards)
    yeet = []
    non_Pass_TD = get_non_pass_TD()
    for i in range(len(player_Names)):
        #Generate a player name, search all arrays for that name, then get the result for that name or put 0 down
        yeet.append([player_Names[i]])
        yeet[i].append(",")
        for j in range(len(pass_yards)):
            if pass_yards[j][0] == player_Names[i]:
                yeet[i].append(round(float(pass_yards[j][1]),2))
                yeet[i].append(",")
                break
            elif j == len(pass_yards)-1:
                yeet[i].append(0)
                yeet[i].append(",")
        for j in range(len(pass_TDs)):
            if pass_TDs[j][0] == player_Names[i]:
                yeet[i].append(round(float(pass_TDs[j][1]),2))
                yeet[i].append(",")
                break
            elif j == len(pass_TDs)-1:
                yeet[i].append(0)
                yeet[i].append(",")
        for j in range(len(rush_yards)):
            if rush_yards[j][0] == player_Names[i]:
                yeet[i].append(round(float(rush_yards[j][1]),2))
                yeet[i].append(",")
                break
            elif j == len(rush_yards)-1:
                yeet[i].append(0)
                yeet[i].append(",")
        for j in range(len(receiving_yards)):
            if receiving_yards[j][0] == player_Names[i]:
                yeet[i].append(round(float(receiving_yards[j][1]),2))
                yeet[i].append(",")
                break
            elif j == len(receiving_yards)-1:
                yeet[i].append(0)
                yeet[i].append(",")
        for j in range(len(receptions)):
            if receptions[j][0] == player_Names[i]:
                yeet[i].append(round(float(receptions[j][1]),2))
                yeet[i].append(",")
                break
            elif j == len(receptions)-1:
                yeet[i].append(0)
                yeet[i].append(",")

        for j in range(len(non_Pass_TD)):
            if non_Pass_TD[j][0] == player_Names[i]:
                yeet[i].append(round(float(non_Pass_TD[j][1]),2))
                yeet[i].append(",")
                break
            elif j == len(non_Pass_TD)-1:
                yeet[i].append(0)
                yeet[i].append(",")

    yeet = get_Points(yeet)
    yeet.insert(0,["Player Name,Passing Yards,Passing TDs,Rushing Yards,Receiving Yards,Receptions,Rush/Rec TD,Points"])
    export_file = open("fantasy.csv", "w")
    for i in range(len(yeet)):
        for j in range(len(yeet[i])):
            yeet[i][j] = str(yeet[i][j])

    for i in range(len(yeet)):
        export_file.writelines(yeet[i])
        export_file.write("\n")


def get_Points(yeet):
    for i in range(len(yeet)):
        points = (0.04 * float(yeet[i][2])) + (6 * float(yeet[i][4])) + (.1 * float(yeet[i][6])) + (.1 * float(yeet[i][8])) + (1 * float(yeet[i][10]) + (6 * float(yeet[i][12])))
        yeet[i].append(round(points,2))
    return yeet

create_CSV()
#print(get_receptions())




