from Application.app import Alex
import json

config_file = r"./Configuration/conf.json"

try:
    conf = open(config_file).read()
    conf = json.loads(conf)
except:
    print("Error while reading configuration file")
    
    a = Alex(conf)
    while True:
        query = a.takeCommand()
        a.analyseQuery(query)

