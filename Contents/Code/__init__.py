# __author__ = 'traitravinh'
import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
################################## MoviHD #########################################
NAME = "MoviHD.net"
BASE_URL = "http://movihd.net"
DEFAULT_ICO = 'icon-default.png'
SEARCH_ICO = 'icon-search.png'
NEXT_ICO = 'icon-next.png'
##### REGEX #####

# ###################################################################################################

def Start():
    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['X-Requested-With'] = 'XMLHttpRequest'
####################################################################################################

@handler('/video/movihd', NAME)
def MainMenu():
    oc = ObjectContainer()
    try:
        link = HTTP.Request(BASE_URL,cacheTime=3600).content
        soup = BeautifulSoup(link)
        catli = soup('li')
        for li in range(0,34):
            lisoup = BeautifulSoup(str(catli[li]))
            lititle = str(lisoup('a')[0].contents[0])
            if lititle==' ':
                lititle = lisoup('a')[0].next.next.next
            lilink = BASE_URL+lisoup('a')[0]['href']
            if lititle.find('PHIM B')!=-1:
                oc.add(DirectoryObject(
                    key=Callback(Servers, title=lititle, slink=lilink, sthumb=R(DEFAULT_ICO)),
                    title=lititle.decode('utf-8'),
                    thumb=R(DEFAULT_ICO)
                ))
            else:
                oc.add(DirectoryObject(
                    key=Callback(Category, title=lititle, catelink=lilink, cthumb=R(DEFAULT_ICO)),
                    title=lititle.decode('utf-8'),
                    thumb=R(DEFAULT_ICO)
                ))
    except Exception, ex:
        Log("******** Error retrieving and processing latest version information. Exception is:\n" + str(ex))

    return oc

####################################################################################################
@route('/video/movihd/category')
def Category(title, catelink, cthumb):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(catelink,cacheTime=3600).content
    soup = BeautifulSoup(link)
    blockbase = soup('div',{'class':'block-base movie'})
    for b in blockbase:
        bsoup = BeautifulSoup(str(b))
        btitle = str(bsoup('a')[0]['title'].encode('utf-8'))
        blink = BASE_URL+bsoup('a')[0]['href']
        bimage = BASE_URL+bsoup('img')[0]['src']

        oc.add(createMediaObject(
            url=blink,
            title=btitle,
            thumb=bimage,
            rating_key=btitle
        ))

    pagination = BeautifulSoup(str(soup('div',{'class':'action'})[0]))('a')
    for p in pagination:
        psoup = BeautifulSoup(str(p))
        plink = BASE_URL+psoup('a')[0]['href']
        ptitle = psoup('a')[0].contents[0]

        oc.add(DirectoryObject(
            key=Callback(Category, title=ptitle, catelink=plink, cthumb=cthumb),
            title=ptitle,
            thumb=cthumb
        ))
    return oc

####################################################################################################
@route('/video/movihd/servers')
def Servers(title, slink, sthumb):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(slink,cacheTime=3600).content
    soup = BeautifulSoup(link)
    blockbase = soup('div',{'class':'block-base movie'})
    for b in blockbase:
        bsoup = BeautifulSoup(str(b))
        btitle = str(bsoup('a')[0]['title'].encode('utf-8'))
        blink = BASE_URL+bsoup('a')[0]['href']
        bimage = BASE_URL+bsoup('img')[0]['src']

        oc.add(DirectoryObject(
            key=Callback(Episodes, title=btitle, eplink=blink, epthumb=bimage),
            title=btitle.decode('utf-8'),
            thumb=bimage
        ))

    pagination = BeautifulSoup(str(soup('div',{'class':'action'})[0]))('a')
    for p in pagination:
        psoup = BeautifulSoup(str(p))
        plink = BASE_URL+psoup('a')[0]['href']
        ptitle = psoup('a')[0].contents[0]

        oc.add(DirectoryObject(
            key=Callback(Servers, title=ptitle, slink=plink, sthumb=sthumb),
            title=ptitle,
            thumb=sthumb
        ))
    return oc

@route('/video/movihd/episodes')
def Episodes(title, eplink, epthumb):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(eplink,cacheTime=3600).content
    soup = BeautifulSoup(link)
    episodes =BeautifulSoup(str(soup('div',{'class':'action left'})[0]))('a')

    for e in episodes:
        esoup = BeautifulSoup(str(e))
        elink =BASE_URL+'/playlist/'+re.compile("javascript:PlayFilm\('(.+?)'\)").findall(esoup('a')[0]['href'])[0]+'_server-2.xml'
        etitle = str(esoup('a')[0].contents[0])

        oc.add(createMediaObject(
            url=elink,
            title=etitle,
            thumb=epthumb,
            rating_key=etitle
        ))

    return oc

@route('/video/movihd/createMediaObject')
def createMediaObject(url, title,thumb,rating_key,include_container=False,includeRelatedCount=None,includeRelated=None,includeExtras=None):
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2
    track_object = EpisodeObject(
        key=Callback(
            createMediaObject,
            url=url,
            title=title,
            thumb=thumb,
            rating_key=rating_key,
            include_container=True
        ),
        title = title,
        thumb=thumb,
        rating_key=rating_key,
        items = [
            MediaObject(
                parts=[
                    PartObject(key=Callback(PlayVideo, url=url))
                ],
                container = container,
                video_resolution = '720',
                video_codec = video_codec,
                audio_codec = audio_codec,
                audio_channels = audio_channels
            )
        ]
    )
    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object


@indirect
def PlayVideo(url):
    url = videolinks(url)
    return IndirectResponse(VideoClipObject, key=url)

def videolinks(url):
    if url.find('xml')!=-1:
        xml_link=url
    else:
        xml_link =BASE_URL+'/playlist/'+re.compile('http://movihd.net/phim/(.+?)_').findall(url)[0]+'_server-2.xml'
    link = HTTP.Request(xml_link,cacheTime=3600).content
    # soup = BeautifulSoup(link)
    # media = BASE_URL+soup('item')[0].next.next.next.next['url']
    media = re.compile('"url_path": "(.+?)","bitrate_label"').findall(link)[0]
    return media
####################################################################################################
