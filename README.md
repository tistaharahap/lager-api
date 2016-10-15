# Lager

Lager is the API for the awesome webapp that's rethinking how people approach travel. The API is **NOT** RESTful, instead it uses a specification called [ACTA](https://github.com/tistaharahap/acta/blob/master/acta.md) that leverages events as a source of truth.

## Events [/v1/events]

### Query with Budget [POST]

```
+ Request (application/json)

        {
            "actor": {
                "id": "2fe614af-266b-4773-a066-3b518763380b"
                "kind": "person"
            },
            "action": "query",
            "object": {
                "id": "USD-500",
                "kind": "currency-number"
            },
            "meta": {
                "currency": "USD",
                "number": 500,
                "origin": {
                    "latitude": -6.1273181,
                    "longitude": 106.123123
                }
            }
        }

+ Response 200 (application/json)

        [
            {
                "actor": {
                    "id": "8f07dc44-df69-4e31-9ad9-c2002d95f68a"
                    "kind": "place"
                },
                "action": "query-result",
                "object": {
                    "id": "2fe614af-266b-4773-a066-3b518763380b"
                    "kind": "person"
                },
                "meta": {
                    "coordinates": {
                        "latitude": -6.1273181,
                        "longitude": 106.123123
                    },
                    "tickets": [
                        {}
                    ],
                    "contents": {
                        "see_all_photos": "http://www.tripadvisor.com/LocationPhotos-g60750-d781627-mMCID-The_Grand_Del_Mar-San_Diego_California.html",
                        "reviews": [
                            {
                                "id": "255810672",
                                "lang": "en",
                                "location_id": "781627",
                                "published_date": "2015-02-22T13:34:21-0500",
                                "rating": 5,
                                "helpful_votes": "1",
                                "rating_image_url": "http://www.tripadvisor.com/img/cdsi/img2/ratings/traveler/s5.0-MCID-5.png",
                                "url": "http://www.tripadvisor.com/ShowUserReviews-g60750-d781627-r255810672-The_Grand_Del_Mar-San_Diego_California.html#review255810672",
                                "trip_type": "Couples",
                                "travel_date": "2015-02",
                                "text": "My wife and I wanted to get away for a couple of days for her birthday. We hadn't been to the San Diego area for a while and wanted a place where we could relax, plat golf and be a little pampered...",
                                "user": {
                                    "username": "russell l",
                                    "user_location": {
                                        "id": "32147",
                                        "name": "Camarillo, California"
                                    }
                                },
                                "title": "Hidden wonder",
                                "is_machine_translated": false
                            },
                            {
                                "id": "255451055",
                                "lang": "en",
                                "location_id": "781627",
                                "published_date": "2015-02-20T13:14:22-0500",
                                "rating": 5,
                                "helpful_votes": "5",
                                "rating_image_url": "http://www.tripadvisor.com/img/cdsi/img2/ratings/traveler/s5.0-MCID-5.png",
                                "url": "http://www.tripadvisor.com/ShowUserReviews-g60750-d781627-r255451055-The_Grand_Del_Mar-San_Diego_California.html#review255451055",
                                "trip_type": "Friends getaway",
                                "travel_date": "2015-02",
                                "text": "From the Valet to even the managers at the Amaya restaurant the service was impeccable.  I loved that all staff took care of tables.  Even the managers where going around and get drink orders and...",
                                "user": {
                                    "username": "James A",
                                    "user_location": {
                                        "id": "32978",
                                        "name": "Riverside, California"
                                    }
                                },
                                "title": "Service was unbelievable.  Great weekend getaway",
                                "is_machine_translated": false
                            },
                            {
                                "id": "255409713",
                                "lang": "en",
                                "location_id": "781627",
                                "published_date": "2015-02-20T09:39:59-0500",
                                "rating": 5,
                                "helpful_votes": "4",
                                "rating_image_url": "http://www.tripadvisor.com/img/cdsi/img2/ratings/traveler/s5.0-MCID-5.png",
                                "url": "http://www.tripadvisor.com/ShowUserReviews-g60750-d781627-r255409713-The_Grand_Del_Mar-San_Diego_California.html#review255409713",
                                "trip_type": "Business",
                                "travel_date": "2015-02",
                                "text": "We were very lucky and enjoyed 4 days of warmth and sunshine poolside where the service is fabulous.  They get your chaise ready for you, bring you ice water and had a wonderful poolside menu (fish...",
                                "user": {
                                    "username": "Terri S",
                                    "user_location": {
                                        "id": "53154",
                                        "name": "Meadowbrook, Pennsylvania"
                                    }
                                },
                                "title": "Beautiful Property",
                                "is_machine_translated": false
                            }
                        ],
                        "web_url": "http://www.tripadvisor.com/Hotel_Review-g60750-d781627-Reviews-mMCID-The_Grand_Del_Mar-San_Diego_California.html",
                        "percent_recommended": null,
                        "location_string": "San Diego, California",
                        "location_id": "781627",
                        "write_review": "http://www.tripadvisor.com/UserReview-g60750-d781627-mMCID-The_Grand_Del_Mar-San_Diego_California.html",
                        "price_level": "$$$$",
                        "review_rating_count": {
                            "1": "6",
                            "2": "8",
                            "3": "22",
                            "4": "65",
                            "5": "875"
                        },
                        "address_obj": {
                            "street1": "5300 Grand Del Mar Court",
                            "street2": "",
                            "city": "San Diego",
                            "state": "California",
                            "country": "United States",
                            "postalcode": "92130",
                            "address_string": "5300 Grand Del Mar Court, San Diego, CA 92130"
                        },
                        "category": {
                            "name": "hotel",
                            "localized_name": "Hotel"
                        },
                        "subratings": [
                            {
                                "localized_name": "Sleep Quality",
                                "rating_image_url": "http://e2.tacdn.com/img2/ratings/traveler/ss5.0.gif",
                                "name": "rate_sleep",
                                "value": "5.0"
                            },
                            {
                                "localized_name": "Location",
                                "rating_image_url": "http://e2.tacdn.com/img2/ratings/traveler/ss4.5.gif",
                                "name": "rate_location",
                                "value": "4.5"
                            },
                            {
                                "localized_name": "Rooms",
                                "rating_image_url": "http://e2.tacdn.com/img2/ratings/traveler/ss5.0.gif",
                                "name": "rate_room",
                                "value": "5.0"
                            },
                            {
                                "localized_name": "Service",
                                "rating_image_url": "http://e2.tacdn.com/img2/ratings/traveler/ss5.0.gif",
                                "name": "rate_service",
                                "value": "5.0"
                            },
                            {
                                "localized_name": "Value",
                                "rating_image_url": "http://e2.tacdn.com/img2/ratings/traveler/ss4.5.gif",
                                "name": "rate_value",
                                "value": "4.5"
                            },
                            {
                                "localized_name": "Cleanliness",
                                "rating_image_url": "http://e2.tacdn.com/img2/ratings/traveler/ss5.0.gif",
                                "name": "rate_cleanliness",
                                "value": "5.0"
                            }
                        ],
                        "trip_types": [
                            {
                                "localized_name": "Business",
                                "name": "business",
                                "value": "209"
                            },
                            {
                                "localized_name": "Couples",
                                "name": "couples",
                                "value": "373"
                            },
                            {
                                "localized_name": "Solo travel",
                                "name": "solo",
                                "value": "17"
                            },
                            {
                                "localized_name": "Family",
                                "name": "family",
                                "value": "275"
                            }
                        ],
                        "awards": [
                            {
                                "award_type": "Traveler's Choice",
                                "year": "2015",
                                "images": {
                                    "tiny": "http://www.tripadvisor.com/img/cdsi/img2/awards/tchotel_tiny-MCID-5.png",
                                    "small": "http://www.tripadvisor.com/img/cdsi/img2/awards/tchotel_2015_L_R-MCID-5.jpg",
                                    "large": "http://www.tripadvisor.com/img/cdsi/img2/awards/TC_2015_downloadable_L_R-MCID-5.jpg"
                                },
                                "categories": [
                                    "Top Hotels",
                                    "Luxury"
                                ],
                                "display_name": "Traveler's Choice"
                            },
                            {
                                "award_type": "GreenLeader",
                                "year": "",
                                "images": {
                                    "small": "http://www.tripadvisor.com/img/cdsi/img2/awards/greenleader_small-MCID-5.gif",
                                    "large": "http://www.tripadvisor.com/img/cdsi/img2/awards/greenleaders/GreenLeaders_API_en_large_silver-MCID-5.jpg"
                                },
                                "categories": [
                                    "Silver level"
                                ],
                                "display_name": "GreenLeader Silver"
                            },
                            {
                                "award_type": "Certificate of Excellence",
                                "year": "2014",
                                "images": {
                                    "small": "http://www.tripadvisor.com/img/cdsi/img2/awards/CERTIFICATE_OF_EXCELLENCE_small-MCID-5.jpg",
                                    "large": "http://www.tripadvisor.com/img/cdsi/img2/awards/CERTIFICATE_OF_EXCELLENCE_2014_en_US_large-MCID-5.jpg"
                                },
                                "categories": [],
                                "display_name": "Certificate of Excellence 2014"
                            }
                        ],
                        "num_reviews": "976",
                        "subcategory": [
                            {
                                "name": "hotel",
                                "localized_name": "Hotel"
                            }
                        ],
                        "rating_image_url": "http://www.tripadvisor.com/img/cdsi/img2/ratings/traveler/5.0-MCID-5.png",
                        "name": "The Grand Del Mar",
                        "ancestors": [
                            {
                                "abbrv": null,
                                "level": "Municipality",
                                "name": "San Diego",
                                "location_id": "60750"
                            },
                            {
                                "abbrv": "CA",
                                "level": "State",
                                "name": "California",
                                "location_id": "28926"
                            },
                            {
                                "abbrv": null,
                                "level": "Country",
                                "name": "United States",
                                "location_id": "191"
                            }
                        ],
                        "longitude": "-117.19746",
                        "rating": "5.0",
                        "latitude": "32.938343",
                        "photo_count": "350",
                        "ranking_data": {
                            "geo_location_id": "60750",
                            "ranking_string": "#1 of 270 hotels in San Diego",
                            "geo_location_name": "San Diego",
                            "ranking_out_of": "270",
                            "ranking": "1"
                        }
                    }
                }
            }
        ]
```

