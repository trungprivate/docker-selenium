#!/bin/bash

# Define the endpoint URL
endpoint="http://grid.aks2.sonarazure.com.au/status"

# Define your username and password
username="sonar"
password="sonar"

# Create the Basic Authentication header
auth_header=$(echo -n "$username:$password" | base64)

# Make the GET request using curl
response=$(curl -s -H "Authorization: Basic $auth_header" -H "X-REGISTRATION-SECRET:" "$endpoint")

# Use jq to filter nodes with availability "UP" and extract relevant information
up_nodes=$(echo "$response" | jq -c '.value.nodes[] | select(.availability == "UP")')

echo $up_nodes

# Loop through each node in up_nodes
echo "$up_nodes" | while IFS= read -r node; do
    # Extract and print relevant information from the node
    id=$(echo "$node" | jq -r '.id')
    
done
