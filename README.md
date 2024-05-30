# NetflixAPI
Follow the below steps to run the application and make a search engine out of **Netflix** data
## Step-1 : 
Clone or Download the repo to your local machine
## Step-2 : 
Install Elasticsearch and cURL latest versions in your machine, (if you want to make requests using Kibana install that too)
## Step-3 : 
Index the **netflixData.json** file using the command
> curl.exe -X PUT "http://localhost:9200/_bulk" -H 'Content-Type: application/json' --data-binary `@netflixData.json

You can also use the command
> curl -X PUT "http://localhost:9200/_bulk" -H 'Content-Type: application/json' --data-binary `@netflixData.json

To test the status of Indexing you have done, go to http:localhost:9200/netflix/video/id where id is a number between 1 and 7787
## Step-4 :
Run the files **api.py** and **app.py**
## Step-5 : 
Go to http://localhost:5000

## NOTE
The working of the app can be found [here](https://github.com/nagendar-pm/NetflixAPI/blob/main/netflixAPI-Doc.pdf)
