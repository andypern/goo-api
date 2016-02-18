import pprint

from googleapiclient.discovery import build


QPX_API_VERSION = 'v1'
DEVELOPER_KEY_FILE =  "/Users/apernsteiner/Desktop/GCE/flight.key"

fh = open(DEVELOPER_KEY_FILE, 'r')

dev_key = fh.read()

def main():
  """get flight stuff
  """
  client = build('qpxExpress', QPX_API_VERSION, developerKey=dev_key)
  resource = client.trips()
  request = resource.search(body=
         {
      "request": {
        "slice": [
          {
            "origin": "JFK",
            "destination": "CDG",
            "date": "2016-02-24"
          }
        ],
        "passengers": {
          "adultCount": 1,
          "infantInLapCount": 0,
          "infantInSeatCount": 0,
          "childCount": 0,
          "seniorCount": 0
        },
        "solutions": 20
      }
    }
  )

  response = request.execute()
  pprint.pprint(response)

  
if __name__ == '__main__':
  main()


  # resource = client.
  # request = resource.list(source='public', country='US')
  # response = request.execute()
  # pprint.pprint(response)

