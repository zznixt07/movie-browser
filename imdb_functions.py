from imdbpie import Imdb
import json

def getFullDetails(resp):
    # print(resp['originalTitle'], resp['id'])
    nullValue = None
    maxShown = 3
    try: plot = resp['plot']['outline']['text']
    except KeyError: plot = nullValue
    try: country = resp['origins'][:maxShown]
    except KeyError: country = []
    try: cast = [mainCast['name'] for mainCast in resp['principals']][:maxShown]
    except KeyError: cast = []
    try: directors = [name['name'] for name in resp['directors']][:maxShown]
    except KeyError: directors = []
    try: writers = [name['name'] for name in resp['directors']][:maxShown]
    except KeyError: writers = []
    # try: 
    # except KeyError: 
    # print(resp)
    isSeries = resp['titleType'] != 'movie'
    if isSeries:
        start = resp['seriesStartYear'] or nullValue
        # when series is still going, no end key
        try: end = resp['seriesEndYear']
        except KeyError: end = nullValue
        epNum = resp['numberOfEpisodes']
        try:
            resp['seasonsInfo']
            szNum = len(resp['seasonsInfo'])
        except KeyError: szNum = nullValue
    else:
        start = nullValue
        end = nullValue
        epNum = nullValue
        szNum = nullValue
    return {
        'imdbId': resp['id'].split('/')[2],
        'imgUrl': resp['image']['url'] or nullValue,
        'title': resp['originalTitle'] or nullValue,
        'rating': resp['rating'] or nullValue,
        'totalRatedBy': resp['numberOfVotes'] or nullValue,
        'year': resp['year'] or nullValue,
        'genres': resp['genres'] or [],
        'isSeries': isSeries,
        'start': start,
        'end': end,
        'epNum': epNum,
        'szNum': szNum,
        'country': country,
        'cast': cast,
        'plot': plot,
        'directors': directors,
        'writers': writers,
    }


class CustomImdb(Imdb):

    def __init__(self):
        Imdb.__init__(self)

    def get_top_rated(self):
        entries = self._get_resource('/chart/ratings/top')['ratings']
        moviesLst = []
        for page, entry in enumerate(entries, start=1):
            imdbId = entry['id'].split('/')[2]
            imgHeight = entry['image']['height']
            imgWidth = entry['image']['width']
            imgUrl = entry['image']['url']
            # returns original title eg:`la casa de papel` instead of `money heist`
            title = entry['title']
            isSeries = entry['titleType'] == 'movie'
            year = entry['year']
            rating = entry['rating']
            totalRatedBy = entry['ratingCount']
            moviesLst.append({
                'imdbId': imdbId,
                'title': title,
                'rating': rating,
                'imgUrl': imgUrl,
                # 'imgHeight': imgHeight,
                # 'imgWidth': imgWidth,
                # 'isSeries': isSeries,
                # 'year': year,
                # 'totalRatedBy': totalRatedBy,
            })
                
        return moviesLst

if __name__ == '__main__':
    imdb = CustomImdb()
    lst = []
    # print(imdb.get_title_auxiliary('tt0120815')['outline']['text'])

    for mov in imdb.get_top_rated()[:20]:
        lst.append(getFullDetails(imdb.get_title_auxiliary(mov['imdbId'])))
    # print(lst)
    
    with open('20mov.json', 'w') as f:
        f.write(json.dumps(lst))
    # with open('20mov.json') as f:
    #     values = [movDict.values() for movDict in json.loads(f.read())]
    # print(values)