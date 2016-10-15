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
                    "contents": {}
                }
            }
        ]
```

