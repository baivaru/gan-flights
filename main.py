import requests
# pip install lxml; html.parser is weird
import lxml
# pip install beautifulsoup4
from bs4 import BeautifulSoup as bs

# pip install fastapi, pip install uvicorn (for local server), pip install jinja2 (for templates)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# create the app
app = FastAPI()
templates = Jinja2Templates(directory="templates")


async def scrape_data():
    # initial data request
    req = requests.get("https://www.ganairport.com/flight-informations")
    # soupify data
    soup = bs(req.content, "lxml")

    # find those weird arrival and departure tables
    table = soup.find_all(
        "table", {"id": "mytable", "style": "white-space:nowrap;width:100%;"})

    # initialize empty lists for arrivals and departures
    arrivals = []
    departures = []

    # find all the rows in the arrival table
    arrival_rows = table[0].tbody.find_all("tr", {"style": "border:none"})

    # do the thing for each arrival row; don't ask me why this is the way it is
    for arrival_row in arrival_rows:
        arrival_cols = arrival_row.find_all("td", {"style": "width:50%"})
        arrival_col_data = [ele.text.strip() for ele in arrival_cols]
        if len(arrival_col_data) == 8:
            if arrival_col_data[0] != "":
                arrivals.append({
                    "airline": arrival_col_data[0],
                    "flight": arrival_col_data[1],
                    "date": arrival_col_data[2],
                    "time": arrival_col_data[3],
                    "origin": arrival_col_data[4],
                    "aircraft": arrival_col_data[5],
                    "belt": arrival_col_data[6],
                    "status": arrival_col_data[7]
                })

    # do the thing for each departure row; don't ask me why this is the way it is
    departure_rows = table[1].tbody.find_all("tr")
    for departure_row in departure_rows:
        departure_cols = departure_row.find_all("td")
        departure_col_data = [ele.text.strip() for ele in departure_cols]
        if len(departure_col_data) == 8:
            if departure_col_data[0] != "":
                departures.append({
                    "airline": departure_col_data[0],
                    "flight": departure_col_data[1],
                    "date": departure_col_data[2],
                    "time": departure_col_data[3],
                    "origin": departure_col_data[4],
                    "aircraft": departure_col_data[5],
                    "belt": departure_col_data[6],
                    "status": departure_col_data[7]
                })

    return (arrivals, departures)


# homepage
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    arrivals, departures = await scrape_data()
    return templates.TemplateResponse('index.html', {'request': request, "arrivals": arrivals, "departures": departures})


# fastapi endpoint
@app.get("/api/")
async def root():
    # get the data
    arrivals, departures = await scrape_data()
    # return the data
    return {
        'app': 'Gan-Flights',
        'description': 'List of upcoming flights from Gan Airport',
        'version': '0.0.1',
        'project': 'https://github.com/baivaru/gan-flights',
        'author': 'Mohamed Aruham',
        'departures': departures,
        'arrivals': arrivals
    }
