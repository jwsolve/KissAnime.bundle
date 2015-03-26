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
ART = "art-default.jpg"
BASE_URL = "http://kissanime.com"
SEARCH_URL = "http://kissanime.com/Search/Anime"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON_SERIES)
	VideoClipObject.thumb = R(ICON_SERIES)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	HTTP.Headers['Host'] = "kissanime.com"
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	return Shows()

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/shows")	
def Shows():

	oc = ObjectContainer()
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search Kisscartoon', prompt='Search for...'))
	html = HTML.ElementFromURL(BASE_URL + '/AnimeList')

	for each in html.xpath("//div[@class='alphabet']/a"):
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
@route(PREFIX + "/showcartoons")	
def ShowCartoons(title, url, page_count):

	oc = ObjectContainer(title1 = title)
	thisurl = url
	thisletter = url.split("=",1)[1]
	html = HTML.ElementFromURL(BASE_URL + '/AnimeList' + url + '&page=' + page_count)

	for each in html.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		thumbhtml = HTML.ElementFromURL(BASE_URL + url)
		thumb = thumbhtml.xpath("//div[@class='barContent']/div/img/@src")[0]
		title = thumbhtml.xpath("//a[@class='bigChar']/text()")[0]
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
	html = HTML.ElementFromURL(BASE_URL + url)
	for each in html.xpath("//table[@class='listing']/tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		thumbhtml = HTML.ElementFromURL(BASE_URL + url)
		title = thumbhtml.xpath("//option[@selected='selected']/text()")[0]
		thumb = thumbhtml.xpath("//meta[@property='og:image']/@content")[0]
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
	page = HTML.ElementFromURL(BASE_URL + url)
	title = page.xpath("//option[@selected='selected']/text()")[0]
	description = page.xpath("//meta[@name='description']/@content")[0]
	thumb = page.xpath("//meta[@property='og:image']/@content")[0]
	
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
	data = HTTP.Request(SEARCH_URL + '?keyword=%s' % String.Quote(query, usePlus=True), headers="").content

	html = HTML.ElementFromString(data)

	for each in html.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		thumbhtml = HTML.ElementFromURL(BASE_URL + url)
		title = thumbhtml.xpath("//a[@class='bigChar']/text()")[0]
		try:
			thumb = thumbhtml.xpath("//div[@class='barContent']/div/img/@src")[0]
		except:
			thumb = ICON_SERIES
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	return oc
