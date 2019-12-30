from Application.app import NewsSentimentAnalysis
import time

conf_file = r"configuration/conf.json"
query = "Trump impeachment"

a = NewsSentimentAnalysis(conf_file)

start_time = time.time()
data = a.pipeline(query)

end_time = time.time()
print("Time for execution: {}".format(end_time-start_time))

# print(data)