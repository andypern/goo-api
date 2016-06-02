import pprint

from googleapiclient.discovery import build


QPX_API_VERSION = 'v1'
DEVELOPER_KEY_FILE =  "/Users/andypern/Desktop/GCE/flight.key"

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
            "origin": "BOS",
            "destination": "PVG",
            "date": "2016-09-27"
          },
          {
            "origin": "PVG",
            "destination": "BOS",
            "date": "2016-10-07"
          },

        ],
        "passengers": {
          "adultCount": 1,
          "infantInLapCount": 0,
          "infantInSeatCount": 0,
          "childCount": 0,
          "seniorCount": 0
        },
        "solutions": 100
      }
    }
  )

  response = request.execute()
  #pprint.pprint(response)

  for trip in response['trips']['tripOption']:
    pprint.pprint(trip)
    #########
    #pricing
    #
    totalPrice =  trip['saleTotal']
    print totalPrice
    #
    #now dig into the details on the pricing
    # you get trip['pricing'] as an array, although it only has 1 element (dict)
    #
    #for prices in trip['pricing']:




    #each segment becomes a slice i believe..

    #for tripSlice in trip['slice']:
    #  print tripSlice['']



    # airline = tripSlice['carrier']
    # fare = trip['saleFareTotal']
    # tax = trip['saleTaxTotal']
    # print "found this: %s , %s , %s, %s" %(totalPrice, airline, fare, tax)

if __name__ == '__main__':
  main()


    # resource = client.
    # request = resource.list(source='public', country='US')
    # response = request.execute()
    # pprint.pprint(response)

