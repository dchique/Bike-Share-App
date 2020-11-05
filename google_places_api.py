from googleplaces import GooglePlaces



def query_gp(search):
    API_KEY = 'AIzaSyAWvf850SYTek9H6IewfDRr5tvTGjyR44Y'
    google_places = GooglePlaces(API_KEY)

    query_result = google_places.nearby_search(
        lat_lng={"lat":40.748,"lng":-73.986},  radius=16000,
        name=search
    )
    return query_result

if __name__ == '__main__':
    result = query_gp('200 Park Ave')
    test = 1
