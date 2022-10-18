import haversine as hs
import math
import numpy as np
import pandas as pd

from http import server

SERVERS_FILE = "/Users/sha/Downloads/servers-2020-07-19.csv"
PINGS_FILE = "/Users/sha/Downloads/pings-2020-07-19-2020-07-20.csv"
PINGS_GROUPED_FILE = "/Users/sha/Downloads/pings-2020-07-19-2020-07-20-grouped.csv"

# get servers of interest based on location from list of all servers
def getServers(geoInput):
    geoLocations = list(geoInput.keys())
    servers = pd.read_csv(SERVERS_FILE)[['id', 'name', 'latitude', 'longitude']]
    selected_servers = servers[ servers['id'].isin(geoLocations) ]
    # selected_servers.rename(columns = {'id':'account_address'}, inplace = True)
    return selected_servers

# get distance between two points in 2D array
# calculates distance in km using Haversine formulae
def getDistanceMatrix(df):
    dist = pd.DataFrame(columns=df["id"], index=df["id"])
    for source in df.index:
        s_addr = df["id"][source]
        s = (df['latitude'][source], df['longitude'][source])
        for destination in df.index:
            d_addr = df["id"][destination]
            d = (df['latitude'][destination], df['longitude'][destination])
            dist[s_addr][d_addr] = hs.haversine(s, d)         
    return dist


### GDI (GeoSpatial Diversity Index) CALCULATION
def calculateGDI(dist_matrix):    
    servers = list(dist_matrix.columns)
    two_third_threshold = math.ceil(len(servers) * (2/3))
    one_third_threshold = math.ceil(len(servers)/3)
    
    dist_df = pd.DataFrame(columns=['id', 'one_third_dist', 'two_third_dist', 'total_dist', 'rms_one_third_dist', 'rms_two_third_dist', 'rms_total_dist'])
    for addr in servers:
        i =0
        j =0 
        total_dist = 0
        two_third_sum = 0
        one_third_sum = 0
        rms_total_dist = 0
        rms_two_third_sum = 0
        rms_one_third_sum = 0
        for num in sorted(dist_matrix[addr]):
            total_dist = total_dist + num
            rms_total_dist = rms_total_dist + pow(num,2)
            if(i < two_third_threshold):
                two_third_sum = two_third_sum + num
                rms_two_third_sum = rms_two_third_sum + pow(num,2)
            if(j< one_third_threshold):
                one_third_sum = one_third_sum + num
                rms_one_third_sum = rms_one_third_sum + pow(num,2)
            i = i +1
            j = j +1
        rms_total_dist = math.sqrt(rms_total_dist)   
        rms_one_third_sum = math.sqrt(rms_one_third_sum)
        rms_two_third_sum = math.sqrt(rms_two_third_sum)
        dist_df = dist_df.append({'id':addr, 'one_third_dist':one_third_sum, 'two_third_dist':two_third_sum, 'total_dist': total_dist, 'rms_one_third_dist': rms_one_third_sum, 'rms_two_third_dist': rms_two_third_sum, 'rms_total_dist' : rms_total_dist }, ignore_index=True)
    return dist_df

def aggregatePingDelays():
    pings = pd.read_csv(PINGS_FILE)
    # took median to ensure extreme values do not affect the mean
    pings_grouped = pings.groupby(['source', 'destination']).median()
    pings_grouped.to_csv(PINGS_GROUPED_FILE)


def getPingDelay(geoInput):
    pingsDelays = pd.read_csv(PINGS_GROUPED_FILE)
    id = list(geoInput.keys())
    pingsDelays = pingsDelays[pingsDelays.source.isin(id) & pingsDelays.destination.isin(id)].query('source != destination')
    return pingsDelays

# x = pings[pings.destination.isin(id)]
# x = x[x[['source', 'destination']].isin(id).any(axis=1)] 
# print(pings)
# pings['distance'] =  pings.apply(lambda row : dist_matrix.loc[int(row['source']), int(row['destination'])], axis = 1)
    
#########################################
### testing above functions from here ###
#########################################
geoInput = {1: 1, 3: 1, 4: 1, 200: 1}

servers = getServers(geoInput)
print(servers)

dist_matrix = getDistanceMatrix(servers)
print(dist_matrix)

valGDI = calculateGDI(dist_matrix)
print(valGDI)

# if file does not exist, go to this step
# aggregatePingDelays()

pingDelays = getPingDelay(geoInput)
print(pingDelays)