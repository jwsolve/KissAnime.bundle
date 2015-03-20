######################################################################################
#
#	Kiss Anime - v0.10
#
######################################################################################

TITLE = "Kiss Anime"
PREFIX = "/video/kissanime"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_SERIES = "icon-tv.png"
ICON_NEXT = "icon-next.png"
BASE_URL = "http://kissanime.com"
SEARCH_URL = "http://kissanime.com/Search/Anime"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_SERIES)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_SERIES)
	VideoClipObject.art = R(ART)

	HTTP.Headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
	HTTP.Headers['Accept-Encoding'] = "gzip, deflate"
	HTTP.Headers['Accept-Language'] = "en-US,en;q=0.5"
	HTTP.Headers['Cache-Control'] = "max-age=0"
	HTTP.Headers['Connection'] = "keep-alive"
	HTTP.Headers['Cookie'] = "__cfduid=d345202ed3eb4cc8194e92f763bba86511426283176"
	HTTP.Headers['DNT'] = "1"
	HTTP.Headers['Host'] = "kissanime.com"
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; rv:35.0.1) Gecko/20100101 Firefox/35.0.1 anonymized by Abelssoft 1584666243"
	
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
		title = each.xpath("./a/text()")[0]
		url = each.xpath("./a/@href")[0]
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = ICON_SERIES
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
	thumb = html.xpath("//div[@class='barContent']/div[2]/img/@src")[0]
	for each in html.xpath("//table[@class='listing']/tr/td[1]"):
		title = each.xpath("./a/text()")[0]
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
	page = HTML.ElementFromURL(BASE_URL + url)
	description = title
	title = page.xpath("//option[@selected='selected']/text()")[0]
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
		title = each.xpath("./a/text()")[0]
		url = each.xpath("./a/@href")[0]
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = ICON_SERIES
				)
		)
	return oc
