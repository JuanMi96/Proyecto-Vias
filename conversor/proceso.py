# To change this license header, choose License Headers in Project Properties.


gpx_file = open('track1.gpx', 'r')
gpx = gpxpy.parse(gpx_file)
def parse_gpx(gpx_input_file):
    
    lats = []
    lons = []
    elevations = []
    timestamps = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lats.append(point.latitude)
                lons.append(point.longitude)
                elevations.append(point.elevation)
                timestamps.append(point.time)
                   
    output = pd.DataFrame()
    output['latitude'] = lats
    output['longitude'] = lons
    output['elevation'] = elevations
    output['starttime'] = timestamps
    output['stoptime'] = output['starttime'].shift(-1).fillna(method='ffill')
    output['duration'] = (output['stoptime'] - output['starttime']) / np.timedelta64(1, 's') ## duration to seconds
    
    return output
df = parse_gpx(gpx)
df.head()

def create_czml_path(df_input, relative_elevation = False):
    results = []
    
    timestep = 0
    
    for i in df_input.index:
        results.append(timestep)
        results.append(df_input.longitude.ix[i])
        results.append(df_input.latitude.ix[i])
        
        if relative_elevation == True:
            results.append(30) # for use with point = {"heightReference" : "RELATIVE_TO_GROUND"}
        else:
            results.append(df_input.elevation.ix[i])
        
        duration = df_input.duration.ix[(i)]
        timestep += duration
        
    return results
def point_with_trailing_path(df_input, time_multiplier = 1000):
    
    # Store output in array
    czml_output = []

    # Define global variables
    global_id = "document"
    global_name = "projecto POO"
    global_version = "1.0"
    global_starttime = str(min(df_input['starttime'])).replace(" ", "T").replace(".000", "Z")
    global_stoptime = str(max(df_input['stoptime'])).replace(" ", "T").replace(".000", "Z")
    global_availability = global_starttime + "/" + global_stoptime    
    
    # Create packet with global variables
    global_element = {
        "id" : global_id,
        "name" : global_name,
        "version" : global_version,
        "clock": {
            "interval": global_availability,
            "currentTime": global_starttime,
            "multiplier": time_multiplier
        }
    }
    
    # Append global packet to output
    czml_output.append(global_element)
    
    # Define path variables
    path_id = "path"
    path_starttime = str(min(df_input['starttime'])).replace(" ", "T").replace(".000", "Z")
    path_stoptime = str(max(df_input['starttime'])).replace(" ", "T").replace(".000", "Z")
    path_availability = path_starttime + "/" + path_stoptime
    
    # Create path object
    path_object = {
            "id": path_id,

            "availability": path_availability,

            "position": {
                "epoch": path_starttime,
                "cartographicDegrees": create_czml_path(df, relative_elevation=False)
            },

            "path" : {
                "material" : {
                    "polylineOutline" : {
                        "color" : {
                            "rgba" : [255,0,0, 200]
                        },
                        "outlineColor" : {
                            "rgba" : [0,173,253, 200]
                        },
                        "outlineWidth" : 5
                    }
                },
                "width" : 6,
                "leadTime" : 0,
                "trailTime" : 100000,
                "resolution" : 5
            }
        }

    # Append path element to output
    czml_output.append(path_object)
        
    # Define point variable
    point_id = "Point"
    point_starttime = str(min(df_input['starttime'])).replace(" ", "T").replace(".000", "Z")
    point_stoptime = str(max(df_input['starttime'])).replace(" ", "T").replace(".000", "Z")
    point_availability = point_starttime + "/" + point_stoptime
    
    point_object = {
            "id": point_id,

            "availability": point_availability,

            "position": {
                "epoch": point_starttime,
                "cartographicDegrees": create_czml_path(df, relative_elevation=True)
            },

            "point": {
                "color": {
                    "rgba": [255, 255, 255, 255]
                },
                "outlineColor": {
                    "rgba": [0,173,253, 255]
                },
                "outlineWidth":6,
                "pixelSize":8,
                "heightReference" : "RELATIVE_TO_GROUND"
            }   
        }

    czml_output.append(point_object)
    
    return czml_output
czml_output = point_with_trailing_path(df)

with open('ruta.czml', 'w') as outfile:
    json.dump(czml_output, outfile)