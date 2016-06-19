import pprint
import os
import sys
import re
from datetime import datetime
from datetime import timedelta
import random
import getopt


from googleapiclient.discovery import build



#######
# stuff to build in
# * deal with over quota exception and move to next key
#
#
#
#


###############
#fields we care about
#
# * total price , carrier , flight number
# * miles , fareclass, fare-price (pre-tax)
# * cost per mile 
# * layover time
# * layover city
# * aircraft , terminal info

#############
# Stuff we need to get elsewhere
# * alliance
# * mileage earning rates (mqm's, mqd's , RDM's)
# * bonuses (class, cabin, elite)
# * shortest possible flight distance between two cities: otherwise cpm may be misleading
#


#########
# some static variables for now
#
#
# startDate = beginning of potential travel window
# endDate = end of potential travel window.  
# Basically, if you say "i want to be away from home sometime between Nov 1st and Jan 31st" , it will search.
# duration = how long of a trip.  Choose a minimum of 7 or else you probably won't get good RT fares.
# note: script will iterate through a maximum of maxSearch , since google sets a 50/day quota.


keydir = "/Users/andypern/Desktop/GCE/flight"

startDate = '2016-09-15'
endDate = '2017-02-15'
duration = 8
maxSearch = 5




QPX_API_VERSION = 'v1'


#set some defaults


pretend = False
cabin = "BUSINESS"
origin = "NYC"
destination = "PAR"

#
# end variables
##### 



#####get opts
#
#
 

try:
        opts, args = getopt.getopt(sys.argv[1:], "o:d:c:k:p", ["origin=","dest=","cabin=",
          "keyfile=","pretend"])
except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print "wrong option"
        sys.exit(2)


for opt, arg in opts:

  if opt in ('-o', '--origin'):
    origin = arg
  if opt in ('-d', '--dest'):
    destination = arg
  if opt in ('-c', '--cabin'):
    cabin = arg.upper()
  if opt in ('-k','--keyfile'):
    keyfile = arg
  if opt in ('-pretend','--pretend'):
    pretend = True




#
#
#####end opts





def main():

  keylist = key_rotator(keydir)

  #
  #simplest thing for now is to just loop through the keys and perform requests.
  # more elegant way might be to pre-build a dictionary of all our requests, count them, 
  # and figure out if we have enough..
  #
  #
  print keylist
  
  #for now, so we don't break it
  dev_key = keylist[0]

  dateSlider(startDate,endDate,dev_key)

def build_request(depDate,retDate,dev_key):

  if not pretend:

    if "BUSINESS" in cabin:
      #
      #we don't want norweigan or icelandair biz class..
      #
      prohibitedCarriers = [
      "DY",
      "FI"
      ]
    elif "COACH" in cabin:
      prohibitedCarriers = [""]
      print "coach"


    """get flight stuff
    """
    client = build('qpxExpress', QPX_API_VERSION, developerKey=dev_key)
    resource = client.trips()
    request = resource.search(body=
           {
        "request": {
          "slice": [
            {
              "origin": origin,
              "destination": destination,
              "date": depDate,
             "preferredCabin": cabin,
             "prohibitedCarrier": prohibitedCarriers
            },
            {
              "origin": destination,
              "destination": origin,
              "date": retDate,
              "preferredCabin": cabin,
              "prohibitedCarrier": prohibitedCarriers
            },

          ],
          "passengers": {
            "adultCount": 1,
            "infantInLapCount": 0,
            "infantInSeatCount": 0,
            "childCount": 0,
            "seniorCount": 0
          },
          "solutions": 1
        }
      }
    )

    response = request.execute()
    #pprint.pprint(response)

    for trip in response['trips']['tripOption']:
      #pprint.pprint(trip)
      #
      # look here: https://gist.github.com/andypern/901aaf0236d28b4b81872a1bf6bf182c
      # 

      #We need to ultimately add up the # of miles for each segment in order
      #to calculate CPM, so start here
      totalMiles = 0
      totalFlightTime = 0
      totalTripTime = 0

      #
      #########
      #pricing
      #
      totalPrice =  trip['saleTotal']
      print totalPrice
      #we'll get tax & such later


      #
      #now dig into the details on the pricing
      # you get trip['pricing'] as an array, although it only has 1 element (dict)
      #
      #for price in trip['pricing']:
      #  print price

      #
      #probably simplest is to grab out of the 'slice' dict
      #


      for tripSlice in trip['slice']:
        sliceMiles = 0
        sliceMins = 0
        #but first..have to peel open the segment array..
        numSegments =  len(tripSlice['segment'])
        for segment in tripSlice['segment']:
          #
          #get carrier & flight # info
          #
          carrier = segment['flight']['carrier']
          flt_num = segment['flight']['number']
          bookingCode = segment['bookingCode']
          bookingCodeCount = segment['bookingCodeCount']
          print "+%s , %s, %s : %s" %(carrier,flt_num,bookingCode,bookingCodeCount)
          
          #
          #each segment is made of 1 or more legs, but most of the time just 1
          #
          for leg in segment['leg']:

            #
            #mainly we want duration & mileage
            #
            legMiles = leg['mileage']
            legMins = leg['duration']
            sliceMiles += legMiles
            sliceMins += legMins



            legOrig = leg['origin']
            legDest = leg['destination']
            print "++%s -> %s : %s mins, %s miles" %(legOrig,legDest,legMins,legMiles)

          totalMiles += sliceMiles
          totalTripTime += sliceMins
        
      #####
      #print totals
      #
      #

      #
      #calculate price per mile
      #

      priceRe = re.search('(EUR|USD)([0-9]+\.[0-9]{2})', str(totalPrice))
      priceFloat = float(priceRe.group(2))
      costPerFlown =  priceFloat / totalMiles

      print "+++++%s mins, %s miles , cpm %s+++++" %(totalFlightTime, totalMiles, costPerFlown)


def key_rotator(keydir):

  keys = []

  keyfiles = os.listdir(keydir)
  for k in keyfiles:
    keyfile = keydir + '/' + k
    fh = open(keyfile, 'r')
    keys.append(fh.read().strip())

  return keys




def dateSlider(startDate,endDate,dev_key):
# thoughts: create while loop until maxSearch is met
# for each iteration, add a random # of days to the startDate , so long as it fits within endDate
# Add 'duration' to randomized startDate , and the resulting pair becomes what gets passed to the request.


#
#date methodology: perhaps figure out the # of days ranging from sDate -> (eDate - duration) as an int
# then find a random date for the newSdate, then convert it to a datetime compatible thing.
#

  sDate = datetime.strptime(startDate, '%Y-%m-%d').date()
  eDate = datetime.strptime(endDate, '%Y-%m-%d').date()

#
#build a random list
#

#find the # of days between start/end
  delta = (eDate - sDate).days
  #build list of random ints that is between two points, but is at most (eDate - duration)

  randList = random.sample(xrange(0, (delta - duration)), maxSearch)



  #
  #iterate
  #
  iteration = 0

  while iteration < maxSearch:

    #
    #figure out where we are in the list
    #
 
    randNum = randList[iteration]

    #once we have a random value, we need to add it to sDate 
    newSdate = sDate + timedelta(days=randNum)
    
    #to get the new end date, simply add duration to newSdate
    newEdate = newSdate + timedelta(days=duration)

    print "%s:%s" %(newSdate,newEdate)

    iteration += 1
  
    #now we can try to execute
    build_request(str(newSdate),str(newEdate),dev_key)




if __name__ == '__main__':

  main()


    # resource = client.
    # request = resource.list(source='public', country='US')
    # response = request.execute()
    # pprint.pprint(response)

