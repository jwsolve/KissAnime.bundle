######################################################################################
#
#	Kiss Anime - v0.10
#
######################################################################################

TITLE = "Kiss Anime"
PREFIX = "/video/kissanime"
ICON = "icon-default.png"
ICON_SERIES = "icon-default.png"
ICON_NEXT = "icon-next.png"
ICON_QUEUE = "icon-cover.png"
ART = "art-default.jpg"
BASE_URL = "http://kissanime.to"
SEARCH_URL = "http://kissanime.to/Search/Anime"

import os
import sys
from lxml import html
import base64

try:
	path = os.getcwd().split("?\\")[1].split('Plug-in Support')[0]+"Plug-ins/KissAnime.bundle/Contents/Code/Modules/KissAnime"
except:
	path = os.getcwd().split("Plug-in Support")[0]+"Plug-ins/KissAnime.bundle/Contents/Code/Modules/KissAnime"
if path not in sys.path:
	sys.path.append(path)

import requests
import cfscrape
scraper = cfscrape.create_scraper()
myrequest = scraper.get(BASE_URL + '/AnimeList')
username = Prefs['username']
password = Prefs['password']

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON_SERIES)
	VideoClipObject.thumb = R(ICON_SERIES)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"

######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	oc = ObjectContainer()
	oc.add(PrefsObject(title=L('preferences')))
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search Kisscartoon', prompt='Search for...'))
	oc.add(DirectoryObject(key = Callback(AToZ), title = "A to Z"))
	oc.add(DirectoryObject(key = Callback(LatestEpisodes, title="Latest Updates", url = '/LatestUpdate', page_count = 1), title = "Latest Updates"))
	oc.add(DirectoryObject(key = Callback(LatestEpisodes, title="Most Popular", url = '/MostPopular', page_count = 1), title = "Most Popular"))
	oc.add(DirectoryObject(key = Callback(LatestEpisodes, title="New Anime", url = '/Newest', page_count = 1), title = "New Anime"))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Bookmarks"), title = "My Bookmarks", thumb = R(ICON_QUEUE)))
	return oc

######################################################################################
# Alphabetical list

@route(PREFIX + "/atoz")
def AToZ():

	oc = ObjectContainer()
	pagehtml = html.fromstring(myrequest.text)
	for each in pagehtml.xpath("//div[@class='alphabet']/a"):
		title = each.xpath("./text()")[0]
		url = each.xpath("./@href")[0]
		if title != "All":
			oc.add(DirectoryObject(
				key = Callback(ShowCartoons, title = title, url = url, page_count = 1),
					title = title,
					thumb = ICON_SERIES
					)
			)
	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/shows")	
def Shows():

	oc = ObjectContainer()
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search Kisscartoon', prompt='Search for...'))
	pagehtml = html.fromstring(myrequest.text)

	for each in page.xpath("//div[@class='alphabet']/a"):
		title = each.xpath("./text()")[0]
		url = each.xpath("./@href")[0]
		oc.add(DirectoryObject(
			key = Callback(ShowCartoons, title = title, url = url, page_count = 1),
				title = title,
				thumb = ICON_SERIES
				)
		)
	return oc

######################################################################################
@route(PREFIX + "/latestepisodes")	
def LatestEpisodes(title, url, page_count):

	oc = ObjectContainer(title1 = title)
	thisurl = url
	thistitle = title
	page = scraper.get(BASE_URL + '/AnimeList' + url + '?page=' + page_count)
	pagehtml = html.fromstring(page.text)

	for each in pagehtml.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/text()")[0]
		thumb = ""
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	oc.add(NextPageObject(
		key = Callback(LatestEpisodes, url = thisurl, title = thistitle, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	return oc

######################################################################################
@route(PREFIX + "/showcartoons")	
def ShowCartoons(title, url, page_count):

	oc = ObjectContainer(title1 = title)
	thisurl = url
	thisletter = url.split("=",1)[1]
	page = scraper.get(BASE_URL + '/AnimeList' + url + '&page=' + page_count)
	htmlpage = html.fromstring(page.text)

	for each in htmlpage.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		thumbhtml = scraper.get(BASE_URL + url)
		page_html = html.fromstring(thumbhtml.text)
		title = page_html.xpath("//a[@class='bigChar']/text()")[0]
		thumb = page_html.xpath("//link/@href")[0]
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	oc.add(NextPageObject(
		key = Callback(ShowCartoons, title = thisletter.upper(), url = thisurl, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	return oc

######################################################################################
@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	page = scraper.get(BASE_URL + url)
	pagehtml = html.fromstring(page.text)
	thisurl = url

	for each in pagehtml.xpath("//table[@class='listing']/tr/td[1]"):
		title = each.xpath("./a/@title")[0].replace('Watch anime','',1).replace('online in high quality','',1)
		thumb = ICON_SERIES
		url = each.xpath("./a/@href")[0]
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page = scraper.get(BASE_URL + url)
	pagehtml = html.fromstring(page.text)
	title = pagehtml.xpath("//option[@selected='selected']/text()")[0]
	description = pagehtml.xpath("//meta[@name='description']/@content")[0]
	thumb = pagehtml.xpath("//meta[@property='og:image']/@content")[0]
	
	oc.add(VideoClipObject(
		title = title,
		summary = description,
		thumb = thumb,
		url = BASE_URL + url
		)
	)	
	
	return oc	

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	searchdata = scraper.get(SEARCH_URL + '?keyword=%s' % String.Quote(query, usePlus=True))

	pagehtml = html.fromstring(searchdata.text)
	for each in pagehtml.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		thumbhtml = scraper.get(BASE_URL + url)
		pagehtml = html.fromstring(thumbhtml.text)
		title = pagehtml.xpath("//a[@class='bigChar']/text()")[0]
		try:
			thumb = pagehtml.xpath("//div[@class='barContent']/div/img/@src")[0]
		except:
			thumb = ICON_SERIES
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	return oc

######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	post_values = {
		'username' : username,
		'password' : password
		}

	if username and password:
		sess = requests.session()
		s = cfscrape.create_scraper(sess)
		page = s.post("http://kissanime.com/Login", post_values)
		#bookmarks = s.get(BASE_URL + '/BookmarkList')
		#pagehtml = html.fromstring(bookmarks.text)
		return MessageContainer(
			"Success",
			page.text
		)
		for each in pagehtml.xpath("//a[@class='aAnime']"):
			url = each.xpath("./@href")[0]
			title = each.xpath("./text()")[0]
			thumb = ""
		
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)
		return oc
	else:
		return MessageContainer(
			"Error",
			"You need to provide a username and password"
		)
