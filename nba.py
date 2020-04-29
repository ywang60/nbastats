import secrets
import json
from bs4 import BeautifulSoup
import requests
import plotly
import sqlite3
import csv
import webbrowser
import plotly.graph_objs as go 

team_url = {'Boston Celtics':'https://www.espn.com/nba/team/stats/_/name/bos/boston-celtics','Brooklyn Nets':'https://www.espn.com/nba/team/stats/_/name/bkn/brooklyn-nets',
'New York Knicks':'https://www.espn.com/nba/team/stats/_/name/ny/new-york-knicks','Philadelphia 76ers':'https://www.espn.com/nba/team/stats/_/name/phi/philadelphia-76ers',
'Toronto Raptors':'https://www.espn.com/nba/team/stats/_/name/tor/toronto-raptors','Chicago Bulls':'https://www.espn.com/nba/team/stats/_/name/chi/chicago-bulls',
'Cleveland Cavaliers':'https://www.espn.com/nba/team/stats/_/name/cle/cleveland-cavaliers','Detroit Pistons':'https://www.espn.com/nba/team/_/name/det/detroit-pistons',
'Indiana Pacers':'https://www.espn.com/nba/team/stats/_/name/ind/indiana-pacers','Milwaukee Bucks':'https://www.espn.com/nba/team/stats/_/name/mil/milwaukee-bucks',
'Denver Nuggets':'https://www.espn.com/nba/team/stats/_/name/den/denver-nuggets','Minnesota Timberwolves':'https://www.espn.com/nba/team/stats/_/name/min/minnesota-timberwolves',
'Oklahoma City Thunder':'https://www.espn.com/nba/team/stats/_/name/okc/oklahoma-city-thunder','Portland Trail Blazers':'https://www.espn.com/nba/team/stats/_/name/por/portland-trail-blazers',
'Utah Jazz':'https://www.espn.com/nba/team/stats/_/name/utah/utah-jazz','Golden State Warriors':'https://www.espn.com/nba/team/stats/_/name/gs/golden-state-warriors',
'LA Clippers':'https://www.espn.com/nba/team/stats/_/name/lac/la-clippers','Los Angeles Lakers':'https://www.espn.com/nba/team/stats/_/name/lal/los-angeles-lakers',
'Phoenix Suns':'https://www.espn.com/nba/team/stats/_/name/phx/phoenix-suns','Sacramento Kings':'https://www.espn.com/nba/team/stats/_/name/sac/sacramento-kings',
'Atlanta Hawks':'https://www.espn.com/nba/team/stats/_/name/atl/atlanta-hawks','Charlotte Hornets':'https://www.espn.com/nba/team/stats/_/name/cha/charlotte-hornets',
'Miami Heat':'https://www.espn.com/nba/team/stats/_/name/mia/miami-heat','Orlando Magic':'https://www.espn.com/nba/team/stats/_/name/orl/orlando-magic',
'Washington Wizards':'https://www.espn.com/nba/team/stats/_/name/wsh/washington-wizards','Dallas Mavericks':'https://www.espn.com/nba/team/stats/_/name/dal/dallas-mavericks',
'Houston Rockets':'https://www.espn.com/nba/team/stats/_/name/hou/houston-rockets','Memphis Grizzlies':'https://www.espn.com/nba/team/stats/_/name/mem/memphis-grizzlies',
'New Orleans Pelicans':'https://www.espn.com/nba/team/stats/_/name/no/new-orleans-pelicans','San Antonio Spurs':'https://www.espn.com/nba/team/stats/_/name/sa/san-antonio-spurs'}

url = "https://free-nba.p.rapidapi.com/players"

querystring = {"page":"10","per_page":"100"}

headers = {
    'x-rapidapi-host': "free-nba.p.rapidapi.com",
    'x-rapidapi-key': secrets.API_KEY
    }

response = requests.request("GET", url, headers=headers, params=querystring).json()

#build a database call NBAdb
#have first table as players, unique key is players' name 
#second table as teams as unique key also as foreign key for the first table

#first step: populating a database
DB_NAME = 'nba.sqlite'
def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_players_sql = 'DROP TABLE IF EXISTS "Players"'
    drop_teams_sql = 'DROP TABLE IF EXISTS "Teams"'
    
    create_players_sql = '''
        CREATE TABLE IF NOT EXISTS "Players" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "first_name" TEXT NOT NULL,
            "last_name" TEXT NOT NULL, 
            "team_full_name" TEXT NOT NULL,
            "Division" TEXT NOT NULL,
            "Abbreviation" TEXT NOT NULL 
        )
    '''
    create_teams_sql = '''
        CREATE TABLE IF NOT EXISTS 'Teams'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'team_full_name' TEXT NOT NULL,
            'link' TEXT NOT NULL
        )
    '''
    cur.execute(drop_players_sql)
    cur.execute(drop_teams_sql)
    cur.execute(create_players_sql)
    cur.execute(create_teams_sql)
    conn.commit()
    conn.close()

def load_teams():
    select_team_sql = '''
        SELECT Id FROM Teams
        WHERE team_full_name = ?
    '''

    insert_teams_sql = '''
        INSERT INTO Teams
        VALUES (NULL, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for c in team_info:
        cur.execute(insert_teams_sql,
            [
                c,
                team_info[c]
            ]
        )
    conn.commit()
    conn.close()

def load_players(): 
    base_url = "https://free-nba.p.rapidapi.com/players"
    querystring = {"page":"0","per_page":"1000"}
    headers = {
        'x-rapidapi-host': "free-nba.p.rapidapi.com",
        'x-rapidapi-key': secrets.API_KEY
        }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    players = response['data']
    insert_player_sql = '''
        INSERT INTO Players
        VALUES (NULL, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for c in players:
        cur.execute(insert_player_sql,
            [
                c['first_name'],
                c['last_name'],
                c['team']['full_name'],
                c['team']['division'],
                c['team']['abbreviation'].lower(),
            ]
        )
    conn.commit()
    conn.close()

file = open('nbateaminfo', 'wb')
writer = csv.writer(file)
team_info = {}
base = 'https://fantasydata.com'
base_url = 'https://fantasydata.com/nba/teams'
response = requests.get(base_url)
soup = BeautifulSoup(response.text,'html.parser')
a = soup.find_all('div', style ='float: left;')
for item in a:
    Name = item.find('a')
    Team_Name = Name.text
    Team_url = Name['href']
    team_info[Team_Name] = base + Team_url


create_db()
load_teams()
load_players()

espnurl = 'https://www.espn.com/nba/team/stats/_/name/bos'
page = requests.get(espnurl)
espnsoup = BeautifulSoup(page.text,'html.parser')

#use team url
GP= []
GS = []
MIN = []
PTS = []
def get_stats(team_url):
    page = requests.get(team_url)
    espnsoup = BeautifulSoup(page.text,'html.parser')
    get_stats = espnsoup.find('div',class_ = 'Table__Scroller').find_all('tr')
    # GP= []
    # GS = []
    # MIN = []
    # PTS = []

    for row in get_stats[1:]:
        stats = row.find_all('td')
        GP.append(stats[0].text)
        GS.append(stats[1].text)
        MIN.append(stats[2].text)
        PTS.append(stats[3].text)
    return GP,GS,MIN,PTS

# get player's name
name= []
def get_names(team_url):
    page = requests.get(espnurl)
    espnsoup = BeautifulSoup(page.text,'html.parser')
    get_names = espnsoup.find('tbody',class_ = 'Table__TBODY')
    a = get_names.find_all('a')
    for row in a:
        name.append(row.text)
    return name



def get_GS_plot(name,GS):
    '''
    params:
    name(list):player's name
    GS(list):player's GS stats
    '''
    xvals = name
    yvals = GS

    scatter_data = go.Scatter(x=xvals, y=yvals)
    basic_layout = go.Layout(title="Athlete's GS Plot")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    fig.write_html("scatter.html", auto_open=True)

def get_GP_plot(name,GP):
    xvals = name
    yvals = GP

    scatter_data = go.Scatter(x=xvals, y=yvals)
    basic_layout = go.Layout(title="Athlete's GP Plot")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    fig.write_html("scatter.html", auto_open=True)

def get_min_plot(name,MIN):
    xvals = name
    yvals = MIN

    scatter_data = go.Scatter(x=xvals, y=yvals)
    basic_layout = go.Layout(title="Athlete'MIN Plot")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    fig.write_html("scatter.html", auto_open=True)

def get_PTS_plot(name,PTS):
    xvals = name
    yvals = PTS

    scatter_data = go.Scatter(x=xvals, y=yvals)
    basic_layout = go.Layout(title="Athlete's PTS Plot")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    fig.write_html("scatter.html", auto_open=True)

b = 1
#which region you want to look at (give the team name for that region)
#which team you want to look at
while b == 1:
    region = input('Which region are you interested in?\n(please select from Central,Atlantic,Southwest,Northwest,Pacific,Southeast)\n')
    if region.lower() == 'central':
        connection = sqlite3.connect("nba.sqlite")
        cursor = connection.cursor()
        query = "SELECT p.team_full_name FROM Players AS P JOIN Teams AS T ON P.team_full_name = T.team_full_name WHERE P.Division = 'Central' GROUP BY P.team_full_name HAVING count(*) > 0"
        result = cursor.execute(query).fetchall()
        connection.close()
        print(result)
        a = 's'
    elif region.lower() == 'atlantic':
        connection = sqlite3.connect("nba.sqlite")
        cursor = connection.cursor()
        query1 = "SELECT p.team_full_name FROM Players AS P JOIN Teams AS T ON P.team_full_name = T.team_full_name WHERE P.Division = 'Atlantic' GROUP BY P.team_full_name HAVING count(*) > 0"
        result1 = cursor.execute(query1).fetchall()
        connection.close()
        print(result1)
        a = 's'
    elif region.lower() == 'southwest':
        connection = sqlite3.connect("nba.sqlite")
        cursor = connection.cursor()
        query2 = "SELECT p.team_full_name FROM Players AS P JOIN Teams AS T ON P.team_full_name = T.team_full_name WHERE P.Division = 'Southwest' GROUP BY P.team_full_name HAVING count(*) > 0"
        result2 = cursor.execute(query2).fetchall()
        connection.close()
        print(result2)
        a = 's'
    elif region.lower() == 'northwest':
        connection = sqlite3.connect("nba.sqlite")
        cursor = connection.cursor()
        query3 = "SELECT p.team_full_name FROM Players AS P JOIN Teams AS T ON P.team_full_name = T.team_full_name WHERE P.Division = 'Northwest' GROUP BY P.team_full_name HAVING count(*) > 0"
        result3 = cursor.execute(query3).fetchall()
        connection.close()
        print(result3)
        a = 's'
    elif region.lower() == 'pacific':
        connection = sqlite3.connect("nba.sqlite")
        cursor = connection.cursor()
        query4 = "SELECT p.team_full_name FROM Players AS P JOIN Teams AS T ON P.team_full_name = T.team_full_name WHERE P.Division = 'Pacific' GROUP BY P.team_full_name HAVING count(*) > 0"
        result4 = cursor.execute(query4).fetchall()
        connection.close()
        a = 's'
        print(result4)
    elif region.lower() == 'southeast':
        connection = sqlite3.connect("nba.sqlite")
        cursor = connection.cursor()
        query5 = "SELECT p.team_full_name FROM Players AS P JOIN Teams AS T ON P.team_full_name = T.team_full_name WHERE P.Division = 'Southeast' GROUP BY P.team_full_name HAVING count(*) > 0"
        result5 = cursor.execute(query5).fetchall()
        connection.close()
        print(result5)
        a = 's'
    elif a == 'exit':
        break
    else:
        print('invalid region. Please enter a valid key.\n')
        a = 'f'
    while a != 'f':
        while True:
            ans = input('Give me your team?(Or enter exit to exit the program)\n')
            if ans in team_info.keys():
                web_cho = input('Do you want to see the page of the team?\n (Enter CR to change region.)')
                if web_cho.lower() == 'yes':
                    retrieving = team_info[ans]
                    webbrowser.open(retrieving)
                elif web_cho.lower() == 'no':
                    ask = input('Do you wanna see the stats plot of your team?\n')
                    if ask.lower() ==  'yes':
                        url = team_url[ans]
                        stats = get_stats(url)
                        name = get_names(url)
                        ask2 = input('Which stats are you interested?\n(select from GP, GS, MIN, PTS)\n')
                        if ask2.lower() == "gp":
                            stat = GP
                            get_GP_plot(name,stat)
                            break
                        elif ask2.lower() == 'gs':
                            get_GS_plot(name,GS)
                            break
                        elif ask2.lower() =='min':
                            get_min_plot(name,MIN)
                            break
                        elif ask2.lower() == 'pts':
                            get_PTS_plot(name,PTS)
                            break
                        else:
                            print('YOU inputed a wrong key')
                    elif ask.lower() == 'no':
                        print('Well, maybe you wanna pick another team or region?\n')
                        break
                elif web_cho.lower() == 'cr':
                    a = 'f'
                    break
                else:
                    print('Please enter a valid key.\n')
                    break
            elif ans == 'exit':
                b = 2
                break
            elif ans not in team_info.keys():
                print('please enter a valid team key. directing you to reselect the region.......')
            break
        break
            