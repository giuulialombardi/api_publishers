import asyncio, tornado

from bson import ObjectId
from pymongo import AsyncMongoClient

async def diz_id_publishers(pubs):
    publishers = pubs.find()
    pub_names_ids = {}
    async for pub in publishers:
        pub_names_ids[pub["name"]] = str(pub["_id"])

class PublisherHandler(tornado.web.RequestHandler):
    async def get(self, id_publisher=None):
        ris_list=[]
        name=self.get_query_argument("name", default=None)
        country=self.get_query_argument("country", default=None)
        if id_publisher:
            ris=await publishers.find_one({"_id": ObjectId(id_publisher)})
            self.set_status(200)
            self.write(str(ris))
        else:
            if name and not country:
                cursore= publishers.find({"name": name})
            elif country and not name:
                cursore = publishers.find({"country": country})
            elif country and name:
                cursore = (publishers.find({"name": name},{"country":country}))
            else:
                ris_list=publishers
            if cursore:
                async for pub in cursore:
                    ris_list.append(pub)
            self.set_status(200)
            self.write(str(ris_list))

    def post(self):
        pass
    def put(self):
        pass
    def delete(self):
        pass

class BookHandler(tornado.web.RequestHandler):
    def get(self):
        pass
    def post(self):
        pass
    def put(self):
        pass
    def delete(self):
        pass


def make_app():
    return tornado.web.Application([
        (r"/publishers", PublisherHandler), #?name e ?country
        (r"/publishers/([0-9a-f]{24})", PublisherHandler),
        (r"/publishers/([0-9a-f]{24})/books", BookHandler), #?title, ?author e ?genre
        (r"/publishers/([0-9a-f]{24})/books/([0-9a-f]{24})", BookHandler)
    ],debug=True)

async def main(shutdown_event):
    app = make_app()
    app.listen(8888)
    print("Server in ascolto su http://localhost:8888/publishers")
    await shutdown_event.wait()
    print("Shutdown ricevuto, chiusura server...")

if __name__ == "__main__":
    client = AsyncMongoClient('localhost', 27017)
    db = client["publisher_db"]
    publishers = db["publishers"]
    books = db["books"]
    shutdown_event = asyncio.Event()
    try:
        asyncio.run(main(shutdown_event))
    except KeyboardInterrupt:
        shutdown_event.set()

