from Application.app import NewsSentimentAnalysis
import time

start = time.time()
conf_file = r"configuration/conf.json"
query = ""
a = NewsSentimentAnalysis(conf_file)

i = 0
data = {}
for item in a.pipeline(query)['articles'][:10]:
    if 'title' in item.keys():
        content = item['content']
        url = item['url']
        temp = a.scrapeWebPage(url)

        if len(content) > 260 and temp:
            more_chars = int(item['content'][263:-7]) + 260
            try :
                start = temp.index(item['content'][:50])
            except:
                start = temp.index(item['title'][50:100])
            end = start + more_chars
            news_data = temp[start:end]
        else:
            news_data = content
        
        clean_title = a.getTwiterQuery(item['title'])
        data[str(i)] = {}
        data[str(i)]['title'] = item['title']
        data[str(i)]['news_data'] = news_data
        data[str(i)]['tweets'] = []
        j = 0
        for result in a.getTweets(clean_title):
            data[str(i)]['tweets'].append({})
            data[str(i)]['tweets'][j]['text'] = result.text
            data[str(i)]['tweets'][j]['location'] = result.user.location
            data[str(i)]['tweets'][j]['friends_count'] = result.user.friends_count
            data[str(i)]['tweets'][j]['favourites_count'] = result.user.favourites_count
            data[str(i)]['tweets'][j]['urls'] = [ item['expanded_url'] for item in result.entities['urls'] ]
            j += 1
        i += 1

end = time.time()
print("Time for execution: {}".format(end-start))

print(data)