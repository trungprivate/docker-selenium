import requests
import base64
import json
import datetime
import logging
import sqlite3
import sys
import time

# set environment variables
nodegraceperiodseconds=300
username = "admin"
password = "NotTelling2021"
base_endpoint = f"https://{username}:{password}@grid.aks.sonarazure.com.au"
frequency=60

# Configure logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s')

# Create a logger instance
logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Connect to NodeDrainCandidate database (or create if it doesn't exist)
conn = sqlite3.connect(':memory:', isolation_level=None)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS nodedraincandidates (id STRING PRIMARY KEY, detectedtime DATETIME)')

# Define the endpoint URLs
status_endpoint = base_endpoint + "/status"
node_endpoint = base_endpoint + "/se/grid/distributor/node"
sessionqueue_endpoint = base_endpoint + "/se/grid/newsessionqueue/queue"

# Create the Basic Authentication header
auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()

# Define headers for the request
headers = {
    "Authorization": f"Basic {auth_header}",
    "X-REGISTRATION-SECRET": "",
}

firstLoop = True

while True:
    # Sleep until the next loop
    if firstLoop: 
        firstLoop = False
    else:
        time.sleep(frequency)
    
    logger.debug("===============================================================")
    logger.debug(f"Starting sweep, frequency set to: {frequency} seconds")
    
    # Get Number of Queued Sessions
    logger.debug("GETTING SESSION COUNT")
    sessionqueue_response = requests.get(sessionqueue_endpoint, headers=headers)
    if sessionqueue_response.status_code == 200:
        sessionqueue_data = sessionqueue_response.json()
        sessionqueue_count = len(sessionqueue_data["value"])
        if not isinstance(sessionqueue_count, (int,float)):
            logger.error("Invalid response received from session queue query: " + sessionqueue_response.text)
            continue
        if sessionqueue_count > 0:
            logger.warning("There are still queued sessions, will not attempt to drain any nodes.")
            continue
        logger.info(f"There are currently {sessionqueue_count} sessions queued, continuing with drain")
    else:
        logger.error("Invalid response received from session queue query: " + sessionqueue_response.text)
        continue

    # Get All Nodes currently registered in Hub
    logger.debug("GETTING NODES CURRENTLY IN THE UP AVAILABILITY STATE")
    hubstatus_response = requests.get(status_endpoint, headers=headers)
    if hubstatus_response.status_code == 200:
        hubstatus_data = hubstatus_response.json()    
        # Filter nodes with availability "UP" and extract relevant information
        up_nodes = [node for node in hubstatus_data["value"]["nodes"] if node["availability"] == "UP"]    
        for node in up_nodes:
            # Insert the node into the nodedraindb if it doesn't already exist
            logger.debug("Inserting Node into the database if it doesn't already exist: " + node["id"])
            cursor.execute("INSERT OR IGNORE INTO nodedraincandidates (id, detectedtime) values(?, ?)", (node["id"], datetime.datetime.now()))
    else:
        logger.error(f"Failed to retrieve status data from hub. Status code: {response.status_code}")
        continue

    # Drain any nodes where grace period has expired
    logger.debug("DRAINING ANY NODES THAT HAVE EXCEEDED THE GRACE PERIOD")
    cursor.execute('SELECT * FROM nodedraincandidates')
    logger.debug("All known nodes waiting for grace period to expire:")
    nodedraincandidates = cursor.fetchall()
    for row in nodedraincandidates:
        logger.debug(row)
        nodeid = row[0]
        # Check if it is still in the list of nodes returned by the hub
        node_still_exists = any(node.get("id") == nodeid for node in up_nodes)
        if not node_still_exists:
            cursor.execute('DELETE FROM nodedraincandidates where id=?',(nodeid,)) 
            logger.info(f"Node with id {nodeid} no longer exists, or is not in the UP state, so removing from DB.")
    threshold_time = datetime.datetime.now() - datetime.timedelta(seconds=nodegraceperiodseconds)
    cursor.execute('SELECT * FROM nodedraincandidates WHERE detectedtime < ?', (threshold_time,))
    results = cursor.fetchall()
    for row in results:
        nodeid = row[0]
        logger.debug("Node to be drained: " + nodeid)
        drain_endpoint = node_endpoint + "/" + nodeid + "/drain"
        drainnode_response = requests.post(drain_endpoint, headers=headers)
        if drainnode_response.status_code == 200:
            logger.info("Drain node successful with node id: " + nodeid)
        else:
            logger.error("Error trying to drain node: " + drainnode_response.text)
        
        cursor.execute('DELETE FROM nodedraincandidates where id=?',(nodeid,))    