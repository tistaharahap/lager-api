from elasticsearch_dsl import DocType, String, Date, Boolean, GeoPoint, analyzer
from datetime import datetime


html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class Article(DocType):
    title = String(analyzer='snowball')
    body = String(analyzer=html_strip)

    airport_code = String(analyzer='snowball')

    location = GeoPoint(lat_lon=True)
    area_name = String(analyzer='snowball')

    created_at = Date()
    published = Boolean()

    class Meta:
        doc_type = 'article'
        index = 'articles'

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)

    @classmethod
    def geosearch(cls, location, distance_in_km=5000):
        distance = '{}m'.format(5000 * 1000)

        return Article().search().filter('geo_distance',
                                         distance=distance,
                                         location=location).execute()
