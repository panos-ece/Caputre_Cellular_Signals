import numpy as np
import folium
from folium.plugins import HeatMap
import sqlite3
from sqlite3 import Error
import os

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM coords")

    rows = cur.fetchall()
    for row in rows:
        print(row)
    return(rows)    

def select_scan_coords(conn):
    cur = conn.cursor()
    cur.execute("SELECT scan_lat, scan_lon FROM coords")

    rows = cur.fetchall()
    return(rows)


database = r"/root/coords.db"

    # create a database connection
conn = create_connection(database)
with conn:
    print("2. Query all tasks")
    rows = select_all_tasks(conn)
    scan_coords = select_scan_coords(conn)
    scan_coords = tuple(set(scan_coords))
    
    print (scan_coords)
    lat_list = []
    for lat in scan_coords:
        lat_list.append(lat[0])

    print(lat_list)

colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred,lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

# create map        
data = (np.random.normal(size=(100, 3)) *
        np.array([[1, 1, 1]]) +
        np.array([[48, 5, 1]])).tolist()
folium_map = folium.Map(location=[39.36345892631218, 22.948074885711076], 
               tiles = 'Stamen Terrain')
#HeatMap(data).add_to(folium_map)
#dct = dict((y, x) for x, y in rows)
#tuple(set(rows)
for row in tuple(set(rows)):
    
    counter = 0
    for lat in lat_list:
        if(lat == row[5]):
            break
        counter += 1
        if(counter == 19):
            counter = 0
    
    if (row[2] == ""):
        provider = "Unknown"
    else:
        provider = str(row[2])
    cel_id= ''
    if(row[3] != ''):
        cel_id = str(row[3])
    else:
        cel_id = "00000"
    folium.Marker(
        location=[row[0], row[1]], # coordinates for the marker (Earth Lab at CU Boulder)
        popup=folium.Popup('<b>provider=</b><br>' + provider + '<br>'
                + '<b>cellid=</b>' + cel_id +'<br>'
                + '<b>freq=</b>' + str(row[4]),min_width = '500%', max_width='500%'), # pop-up label for the marker
        icon=folium.Icon(colors[counter])
    ).add_to(folium_map)

counter = 0
for coords in scan_coords: 
    folium.Marker(
        location=[coords[0], coords[1]], # coordinates for the marker (Earth Lab at CU Boulder)
        popup=folium.Popup("<b>scan_location_%d </b>" % (counter)), # pop-up label for the marker
        icon=folium.Icon(colors[counter], icon='home')
    ).add_to(folium_map)
    counter += 1
# this won't work:
#folium_map
#folium_map.render()



# ------------------------------------------------------------------------------------------------
# so let's write a custom temporary-HTML renderer
# pretty much copy-paste of this answer: https://stackoverflow.com/a/38945907/3494126
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = 7000
HOST = '127.0.0.1'
SERVER_ADDRESS = '{host}:{port}'.format(host=HOST, port=PORT)
FULL_SERVER_ADDRESS = 'http://' + SERVER_ADDRESS


def TemproraryHttpServer(page_content_type, raw_data):
    """
    A simpe, temprorary http web server on the pure Python 3.
    It has features for processing pages with a XML or HTML content.
    """

    class HTTPServerRequestHandler(BaseHTTPRequestHandler):
        """
        An handler of request for the server, hosting XML-pages.
        """

        def do_GET(self):
            """Handle GET requests"""

            # response from page
            self.send_response(200)

            # set up headers for pages
            content_type = 'text/{0}'.format(page_content_type)
            self.send_header('Content-type', content_type)
            self.end_headers()

            # writing data on a page
            self.wfile.write(bytes(raw_data, encoding='utf'))

            return

    if page_content_type not in ['html', 'xml']:
        raise ValueError('This server can serve only HTML or XML pages.')

    page_content_type = page_content_type

    # kill a process, hosted on a localhost:PORT
    subprocess.call(['fuser', '-k', '{0}/tcp'.format(PORT)])

    # Started creating a temprorary http server.
    httpd = HTTPServer((HOST, PORT), HTTPServerRequestHandler)

    # run a temprorary http server
    httpd.serve_forever()


def run_html_server(html_data=None):

    if html_data is None:
        html_data = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Page Title</title>
        </head>
        <body>
        <h1>This is a Heading</h1>
        <p>This is a paragraph.</p>
        </body>
        </html>
        """

    # open in a browser URL and see a result
    webbrowser.open(FULL_SERVER_ADDRESS)

    # run server
    TemproraryHttpServer('html', html_data)

# ------------------------------------------------------------------------------------------------


# now let's save the visualization into the temp file and render it
from tempfile import NamedTemporaryFile
tmp = NamedTemporaryFile()
folium_map.save(tmp.name)
with open(tmp.name) as f:
    folium_map_html = f.read()

run_html_server(folium_map_html)
