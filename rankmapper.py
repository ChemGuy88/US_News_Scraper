#!/usr/bin/python
# -*- coding: utf-8 -*-

# usnews mapper

'''
This project intends to scrape ranks from US News & World Report, then map the schools
# Credit to #https://github.com/Shengjiezh/Scraping-USNews-College-Ranking/blob/master/Usnews.py
'''

import time, requests, re #, winsound
from bs4 import BeautifulSoup


########################################################################
### Universal variables ################################################
########################################################################

ROOT = u'https://www.usnews.com'
UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0)'+\
            ' Gecko/20100101 Firefox/56.0'
Headers = { 'User-Agent': UserAgent}



########################################################################
### Classes ############################################################
########################################################################

class URLS_List(list):
    '''
    Dummy class to allow giving a "name" attribute to lists
    '''
    pass


########################################################################
### Scraping Functions #################################################
########################################################################

# def alarm():
#     duration = 1000  # millisecond
#     freq = 440  # Hz
#     winsound.Beep(fre, duration)

def getHTML(Subject):
    '''
    matches Subject to the URL
    '''
    # Would need to create a dictionary that points each Subject to a USnews URL
    pass

def getLastURL(URL,i=0):
    R = requests.get(URL, headers = Headers)
    soup = BeautifulSoup(R.text, 'lxml')
    Found = soup.findAll('a', href=True, text = u'Next »')
    
    L = []
    if len(Found) > 0:
        Link = ROOT + Found[0]['href']
        time.sleep(0.25)
        i += 1
        return getLastURL(Link, i)
    else:
        return URL

def getURLS(URL,Subject):
    '''
    Tried to do it recursively, which would've been cool, but I couldn't. So I'll just get the last URL and synthesize the previous ones from it
    '''
    LastURL = getLastURL(URL)
    print LastURL
    PageNum = re.findall('page\+(\w+)', LastURL)[0]
    REPS = int( PageNum )
    I = LastURL.find('page')
    Prefix = LastURL[:I]
    
    URLS = URLS_List()
    for PageNum in range(1,REPS):
        PageURL = Prefix + 'page+' + str(PageNum)
        URLS.append(PageURL)
    URLS.append(LastURL)
    
    URLS.name = Subject
    print '\nURLS for %s loaded.\n' % Subject
    return URLS

def Standardize(Department):
    '''
    changes format of string to use in searching tags
    '''
    Department = Department.replace('-',' ')
    Department = Department.replace('&','')
    Department = Department.replace(',','')
    Department = Department.replace('.','')
    Department = Department.lower()
    return Department.strip()

def filterTags(tag):
    '''
    for use in soup.findAll()
    '''
    is_h4 = tag.name == 'h4'
    has_class = tag.has_attr('class')
    if has_class:
        classes = tag['class']
        if len(classes) == 1:
            has_only_mini = classes == ['h-mini']
            return is_h4 and has_class and has_only_mini
    return False

def findTag(soup, Department):
    '''
    finds which tag contains address
    '''
    tags = soup.findAll(filterTags)
    for tag in tags:
        tagString = Standardize(tag.string)
        if tagString == Department:
            return tag
    
    answer = raw_input('Warning, no tag was found for this school. '+\
                       'Continue? y/n.\n')
    if answer == 'y':
        return 'N/A'
    elif answer == 'n':
        sys.exit()
    else:
        raw_input('Invalid input. \'y\' to continue, \'n\' to exit '+\
                  'script.')

def getAddress(school):
    '''
    Uses USNews.com address for school
    '''
    
    Link = school['href']
    Link = ROOT + Link
    R = requests.get(Link, headers=Headers)
    time.sleep(0.05)
    soup = BeautifulSoup(R.text, 'lxml')
    
    # Extract department string
    Department = re.findall('[^/]+?$', Link)[0] # finds all chars except /,
                                                # which are next to the end
                                                # of line
    Department = re.findall('[a-z/-]+', Department)[0]
    Department = Standardize(Department)
    
    # Find tag with matching Department
    tag = findTag(soup, Department)
    try:
        Parent = tag.parent # move up
    except:
        return 'N/A'
    tag = Parent.find('table')
    tag = tag.find('tr')
    tag = tag.findAll('td')
    
    # Extract address
    A = tag[1].text
    B = A.split('\n')
    C = []
    for b in B:
        C.append(b.strip())
    D = []
    for c in C:
        if len(c) > 0:
            D.append(c)
    Address = ', '.join(D)
    # Some schools have two stats departments, the least of which has no address, and only a phone number.
    return Address   

def Scraper(URLS, Subject):
    '''
    Input: Subject, a string,
    Output: A object with the scraped results
    '''
    
    Ranks  = []; Schools  = []; Locations  = []; Addresses  = []
    Ranks1 = []; Schools1 = []; Locations1 = []; Addresses1 = []
    
    i = 0
    for URL in URLS:
        i += 1
        print '\nURL %d of %d\n' % (i, len(URLS))
        R = requests.get(URL, headers=Headers)
        soup = BeautifulSoup(R.text, 'lxml')
        
        Ranks = soup.findAll('span', attrs={'class': 'rankscore-bronze'})
        Schools = soup.findAll('a', attrs={'class': 'school-name'})
        Locations = soup.findAll('p', attrs={'class': 'location'})
        
        for rank in Ranks:
            try:
                TEMP = int( re.findall('\d+', rank.text)[0] )
            except IndexError:
                TEMP = re.findall('\w+', rank.text)[0] 
            Ranks1.append( TEMP )
            
        for school in Schools:
            TEMP = school.text
            Schools1.append( TEMP )
            
            address = getAddress( school )
            Addresses1.append( address )
            
        for location in Locations:
            TEMP = location.text
            Locations1.append( TEMP )
    
    assert len(Ranks1) == len(Schools1) == len(Locations1)
    L = []
    I = len(Ranks1)
    for i in range(I):
        T = ( Ranks1[i], Schools1[i], Locations1[i], Addresses1[i])
        L.append(T)
    
    return L
    
########################################################################
### Meta Functions #####################################################
########################################################################

def cleanString(string):
    '''
    removes nasty characters python can't deal with
    '''
    #string = string.replace('\xe2\x80\x94\xe2\x80\x8b','-')
    string = string.replace(u'\u2014\u200b','-')
    string = string.replace(u'\u200b',' ')
    return string

def saveScrape(L,Subject):
    Ranks = []
    Schools = []
    Locations = []
    Addresses = []
    
    rootSave = '/Users/Herman/Documents/rankmapper/'
    filename = rootSave + Subject + '.txt'
    F = open(filename,'w')
    F.write('Rank;School;City;Address\n')
    for t in L:
        line = '%s;%s;%s;%s\n' % (t[0],t[1],t[2],t[3])
        try:
            F.write( cleanString(line ) )
        except:
            print line

def Mine(URLS, Subject='statistics'):
    Subject = Subject.lower()
    SUBJECT_URL = 'https://www.usnews.com/best-graduate-schools/'+\
                  'top-science-schools/'+Subject+'-rankings'
    
    if not URLS.name == Subject:
        URLS = getURLS(SUBJECT_URL, Subject)
    
    L = Scraper(URLS,Subject)
    saveScrape(L,Subject)
    
    return L

########################################################################
### Variables for troubleshooting ######################################
########################################################################

Subject = 'computer-science'
SUBJECT_URL = 'https://www.usnews.com/best-graduate-schools/'+\
              'top-science-schools/'+Subject+'-rankings'

try:
    type(URLS)
    if not URLS.name == Subject:
        print '\nIncorrect URLS set provided. Supplied links are for'+\
              ' %s, replacing them with correct links for %s\n' %\
               (URLS.name, Subject)
        URLS = getURLS(SUBJECT_URL, Subject)
except NameError:
    URLS = getURLS(SUBJECT_URL, Subject)

# Results = Mine(URLS, 'Statistics') # list of 87
# Chemistry = Mine(URLS, 'Chemistry') # list of 200+
cs = Mine(URLS, 'Computer-science')
# bio = Mine(URLS, 'biological-sciences')

########################################################################
### End of File ########################################################
########################################################################