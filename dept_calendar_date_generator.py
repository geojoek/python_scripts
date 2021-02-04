# Script for generating list of dates for a weekly event that occurs on a given weekday aat a given time
# by Joe Kopera, February, 2021
# written for Python 3.x

import datetime

# parameters woot woot!
startDay = "Feb 1 2021" # date has to be entered in a "Jan 1 2021" format to be parasable by this script
numDays = 100 # number of days out from today

# the list objects you want to dump the days of your given weekday into
tuesdayList = []
tuesdayTime = "6:00 PM" #times have to be in this format to be machine readable by Drupal site I'm importing this into

thursdayList = []
thursdayTime = "6:00 PM"

# the guts of the script:

startDayObject = datetime.datetime.strptime(startDay, "%b %d %Y")
base = datetime.datetime.today()
dateList = [startDayObject + datetime.timedelta(days=x) for x in range(numDays)]

def listbuilder(day, list): # builds the actual list of dates
    for date in dateList:
        if date.weekday() == day:
            dateString = date.strftime("%b %d %Y") # the format this spits out to is machine readable by the Drupal website I import these lists into.
            list.append(dateString)

def printList(list, time): # prints the actual list of dates
    dateObject = datetime.datetime.strptime(list[1], "%b %d %Y")
    print("Dates that fall on {} for time specified".format(dateObject.strftime("%A")))
    for x in list:
)
    print("\n")

# more parameters that you had to add / alter:

listbuilder(1, tuesdayList) # the first number here is the index of the day of the week, with Monday being 0 and Sunday being 6
listbuilder(3, thursdayList)

printList(tuesdayList, tuesdayTime) # this prints the list into the console
printList(thursdayList, thursdayTime)