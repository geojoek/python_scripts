# Script for scraping the Five College Consortium Course Catalog for all courses being offered
# by the Geosciences Department at U-Mass Amherst, and then re-compiling that into a new HTML table
# to copy-paste into the Geosciences Website

# script by Joseph P. Kopera November 2020, updated November 2021
# Written for Python 3.9 in conda environment with Selenium library.

# NOTE: This is scraping an HTML table into a dictionary and then parsing again into another HTML table
# There are definitely more elegant and faster ways of doing this, likely using Regex
# but I wanted to play around with constructing nested dictionaries and also build code that built dictionaries
# in case one needs to parse out courses into something other than HTML.

# NOTE: I'm not explicitely introducing rate limiting into the script even though that is best practice
# the for loop below that extracts data into a dictionary basically accomplishes that function.

# NOTE: For Spring 2021 I had to manually add a dictionary item for the course later in the script.
# Be sure to delete it whenver it finally gets listed in the FCCC or when you use this for a different semester.

#### Parameters
geckoPath = r"/Volumes/Data/Projects/Geosciences_Webpage/scripts/geckodriver" # Path to the gecko driver to run headless Firefox via selenium library
outFileNameAndPath = r"/Volumes/Data/Projects/Geosciences_Webpage/Spring2022_Courses.html" # file you want the HTML dumped into
semester = "S" # S == spring, F == Fall
year = "2022"

#### Setting up selenium to use Firefox headless - Selenium is library that will drive Firefox browser
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
print("Imported python libraries")

options = Options()
options.headless = True # run Firefox headless so it does not load up its GUI
options.add_argument("--window-size=1920,1200")

profile = webdriver.FirefoxProfile()
driver = webdriver.Firefox(options=options, executable_path=geckoPath) # set path to the gecko driver that drives Firefox. Gecko can be downloaded from https://github.com/mozilla/geckodriver
print("Loaded gecko driver for headless Firefox browser")


#### scraping of Five College Consortium Course Catalog
# The FCCC has its query in the URL hash which is super convenient... so we just retrieve a URL with the constructed query we want, for the year and semester described above
constructedURL = "https://www.fivecolleges.edu/courses?field_course_semester_value={}&field_course_year_value={}&field_course_institution_value[]=U&subject_name=GEO".format(semester, year)

# retrieving the page
driver.get(constructedURL) # loads the search results from the above URL
print("Loading {}\n".format(constructedURL))

courseDict = {} # create a dictionary object to put courses into

n = 1
while True: # sets up an endless loop that's contingent on the try / except below for next button.  There have to be more elegant ways of doing this.
    print("Scraping page {} of results".format(n))
    # finds the table with the course information based on xpath I copied from browser > developer tools > inspect element
    courseTable = driver.find_elements_by_xpath("//*[@class=\"tablesaw tablesaw-stack cols-8\"]/tbody/tr")

    # since output from FCC course page table is always the same, we can iterate through the table, extract the course info., and add to a dictionary to parse into HTML later...
    for row in courseTable: # iterates through each row of the table
        # note: I initally tried find_element_by_class_name but since the class name has a space in it, it didn't work.  The following assumes that all the table columns are in the right order which is less than ideal.
        # other note: there's a more elegant and shorter way to do this by finding the table headers and exporting them into a list and doing nested iterations but I'm tired and it feels prone to error when writing the HTML below.
        courseSubject = row.find_element_by_xpath("td[1]").text # this is xpath of this element _within_ each row of the course table.
        courseNumber  = row.find_element_by_xpath("td[2]").text
        sectionNumber = row.find_element_by_xpath("td[3]").text
        dictKey = str(courseSubject) + "-" + str(courseNumber) + "-" + str(sectionNumber)
        #populating the dictionary
        courseDict[dictKey] = {} # creating nested dictionary for each course
        courseDict[dictKey]['courseSubject'] = courseSubject
        courseDict[dictKey]['courseNumber'] = courseNumber
        courseDict[dictKey]['sectionNumber'] = sectionNumber
        courseDict[dictKey]['courseType'] = row.find_element_by_xpath("td[4]").text
        courseTitle = row.find_element_by_xpath("td[5]").text
        courseDict[dictKey]['courseTitle'] = courseTitle
        courseDict[dictKey]['courseURL'] = row.find_element_by_xpath("td[5]").find_element_by_tag_name("a").get_attribute("href")
        courseDict[dictKey]['courseInstructor'] = row.find_element_by_xpath("td[6]").text
        courseDict[dictKey]['courseTime'] = row.find_element_by_xpath("td[8]").text

    try: # Since the results of the search are paginated, this is a crude way of finding the next button
         # and iterating through the multi-page output of the query. It works compared to every other method I've found since the next button
         # is an actual link tag instead of a javascript element
        nextButton = driver.find_element_by_class_name("pager__item--next")
        # Note re: the above line-- this element on this website has multiple class names separated by a space... "pager__item pager__item--next",
        # which is what Web Inspector returns. These are two separate css classes, so either use find_element_by_css_selector
        # or pick the latter and more specific of those two class names.
        print(nextButton)
        nextButtonURL = nextButton.find_element_by_tag_name("a").get_attribute("href")
        driver.get(nextButtonURL) # 'clicks' on the 'next' link
        n = n + 1
    except Exception as e: # when there are no more pages left the script will throw an Exception that it can't find the 'pager-next' class.
        print(e) # Gives us the exception message
        print("Done Scraping and parsing HTML into dictionary")
        driver.quit() # shuts down the headless browser
        break # busts out of the endless loop

### Writing HTML course schedule out to file
import os # File handling
import datetime
now = datetime.datetime.now() # fetching today's date to put into HTML

# iterating through course dictionary created above and filtering out separate dictionaries by course subject
# This is ostensibly faster than using selenium to do this is in for loop above.

# Define function to filter above dictionary
def courseFilter(subjectValue, nameOfSubjectDictionary): # have to be more elegant ways for me to construct a dictionary name from the value of another variable
    nameOfSubjectDictionary = {}
    for courseKey, courseValues in courseDict.items(): # reminder here that this is nested dictionary-- coursKey is each item in courseDict, and courseValues is the inner dictionary of the values for each course
        if courseValues.get('courseSubject') == subjectValue:
            nameOfSubjectDictionary[courseKey] = courseValues
        else:
            pass
    return nameOfSubjectDictionary

# Actually filtering the above dictionaries into three dictionaries
geographyDict = courseFilter("GEOGRAPH", "geographyCourses")
geologyDict = courseFilter("GEOLOGY", "geologyCourses")
geosciDict = courseFilter("GEO-SCI", "geosciencesCourses")

print ("Done filtering dictionary into courses by subject")

# defining function to write HTML out to file
# Note: this requires the dictionaries to already be in some sort of sorted order. I'm counting on scraped HTML to accomplish that.
# This can probably be optimized and _should_ include some sort of sort functionality using the sorted() module and parsing HTML from the resulting lists
# The way you can accomplish this is basically a list of lists, and instead of value.get you retrieve info via their list index position.
# and if that's the case you don't even need to really deal with dictonaries, but they sure are otherwise handy.
def writeHTMLTable(dictionary, subjectName, out):
    out.write("<h2>Courses in {}</h2>\n".format(subjectName))
    out.write("<table>\n<thead>\n<tr>\n<th>Subject</th>\n<th>Course #</th>\n<th>Section #</th>\n<th>Type</th>\n<th>Title</th>\n<th>Instructor</th>\n<th>Time</th>\n</tr>\n</thead>\n<tbody>\n")
    for key, value in dictionary.items():
        out.write("<tr>\n")
        out.write("<td>" + str(value.get('courseSubject')) + "</td>\n")
        out.write("<td>" + str(value.get('courseNumber')) + "</td>\n")
        out.write("<td>" + str(value.get('sectionNumber')) + "</td>\n")
        out.write("<td>" + str(value.get('courseType')) + "</td>\n")
        out.write("<td><a href=\"" + str(value.get('courseURL')) + "\" target=\"_blank\">" + str(value.get('courseTitle')) + "</a></td>\n")
        out.write("<td>" + str(value.get('courseInstructor')) + "</td>\n")
        out.write("<td>" + str(value.get('courseTime')) + "</td>\n")
        out.write("</tr>\n")
    out.write("</tbody>\n</table>")
    return

# Actually writing the HTML out to the file
with open(outFileNameAndPath, 'a', encoding='utf-8') as outFile:
    outFile.write("<p>This list is copied from the Five College Consortium <a href=\"https://www.fivecolleges.edu/academics/courses\" target=\"_blank\"> course schedule</a> and is updated as often as possible.<br>\n ")
    outFile.write("Until the end of Add/Drop, courses are changing daily. Please log into <a href=\"https://www.spire.umass.edu\" target=\"_blank\">SPIRE</a> for the latest course information.<br>\n")
    outFile.write("\n<strong><em>NOTE:</em></strong> Some remote-learning courses may be mistakenly listed as in-person / on-campus on SPIRE. Please contact the instructor for the latest information on how the course will be taught.\n")
    outFile.write("\n<em>This page last updated {}</em></p>\n".format(now.strftime("%m-%d-%Y")))
    writeHTMLTable(geographyDict, "Geography", outFile)
    writeHTMLTable(geologyDict, "Geology", outFile)
    writeHTMLTable(geosciDict, "the Geosciences", outFile)
    print("Written everything to HTML file at {}".format(outFileNameAndPath))
print("All done!")