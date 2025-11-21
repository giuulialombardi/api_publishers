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
                cursore = publishers.find({"name": name},{"country":country})
            else:
                ris_list=publishers
            if cursore:
                async for pub in cursore:
                    ris_list.append(pub)
            self.set_status(200)
            self.write(str(ris_list))


    async def post(self):
        data = tornado.escape.json_decode(self.request.body)
        if data.get("name") and data.get("country") and data.get("founded_year"): #.get perché nel caso non ci fosse la chiave restituisce None e non da errore
            try:
                data["founded_year"] = int(data["founded_year"])
            except TypeError:
                self.set_status(400)
                self.write({"error": "Richiesta errata"})
                return
            await publishers.insert_one({"name": data["name"], "founded_year": data["founded_year"], "country": data["country"]})
            self.set_status(201)
            self.write(data)
        else:
            self.set_status(400)
            self.write({"error": "Richiesta incompleta"})


    async def put(self, id_publisher):
        if id_publisher:
            data = tornado.escape.json_decode(self.request.body)
            if data.get("name") and data.get("country") and data.get(
                    "founded_year"):  # .get perché nel caso non ci fosse la chiave restituisce None e non da errore
                try:
                    data["founded_year"] = int(data["founded_year"])
                except TypeError:
                    self.set_status(400)
                    self.write({"error": "Richiesta errata"})
                    return
                await publishers.update_one({"_id":ObjectId(id_publisher)},{"$set":{"name": data["name"], "founded_year": data["founded_year"], "country": data["country"]}})
                self.set_status(201)
                self.write(data)
            else:
                self.set_status(400)
                self.write({"error": "Richiesta incompleta"})
        else:
            self.set_status(400)
            self.write({"error": "Richiesta incompleta"})


    async def delete(self, id_publisher):
        if id_publisher:
            await publishers.delete_one({"_id": ObjectId(id_publisher)})
            #print(ris.deleted_count)
        else:
            self.set_status(400)
            self.write({"error": "Richiesta incompleta"})


class BookHandler(tornado.web.RequestHandler):
    async def get(self, id_publisher, id_book=None):
        ris_list=[]
        title = self.get_query_argument("title", default=None)
        author = self.get_query_argument("author", default=None)
        genre = self.get_query_argument("genre", default=None)
        if id_publisher:
            if id_book:
                book = await books.find_one({"_id": ObjectId(id_book), "publisher_id": ObjectId(id_publisher)})
                if book:
                    self.set_status(200)
                    self.write(str(book))
                    return
                else:
                    self.set_status(404)
                    self.write({"error": "Libro non trovato"})
                    return
            if title:
                book = await books.find_one({ "title": title, "publisher_id": ObjectId(id_publisher)})
                if book:
                    self.set_status(200)
                    self.write(str(book))
                    return
                else:
                    self.set_status(404)
                    self.write({"error": "Libro non trovato"})
                    return
            if author and not genre:
                book_cursor = books.find({"author": author, "publisher_id": ObjectId(id_publisher)})
                if book_cursor:
                    async for book in book_cursor:
                        ris_list.append(book)
                else:
                    self.set_status(404)
                    self.write({"error": "Autore non trovato"})
            if genre and not author:
                book_cursor = books.find({"genre": genre, "publisher_id": ObjectId(id_publisher)})
                if book_cursor:
                    async for book in book_cursor:
                        ris_list.append(book)
                else:
                    self.set_status(404)
                    self.write({"error": "Genere non trovato"})
            if genre and author:
                book_cursor = books.find({"genre": genre,"author":author, "publisher_id": ObjectId(id_publisher)})
                if book_cursor:
                    async for book in book_cursor:
                        ris_list.append(book)
                else:
                    self.set_status(404)
                    self.write({"error": "Genere non trovato"})
            if len(ris_list)>0:
                self.set_status(200)
                self.write(str(ris_list))
        else:
            self.set_status(400)
            self.write({"error": "Richiesta incompleta"})


    def post(self, id_publisher):



    def put(self, id_publisher, id_book):
        pass


    def delete(self, id_publisher, id_book):
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

