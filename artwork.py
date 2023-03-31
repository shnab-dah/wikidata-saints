from app import *


class Artwork:
    def __init__(self, data):
        self.QID = data.name
        self.objectvalue = data['object.value']
        date = data['dates.value']
        date = date.split('-')
        self.date = date[0]
        self.creators = str(data['creators.value']).split(';')
        self.depictions = str(data['depictions.value']).split(';')
        self.images = str(data['images.value']).split(';')
        self.collection = str(data['collection.value']).split(';')
        self.genres = str(data['genres.value']).split(';')
        self.materials = str(data['materials.value']).split(';')
        self.types = str(data['types.value']).split(';')
        self.creationPlace = str(data['creationPlace.value']).split(';')


if __name__ == "__main__":
    x = Corpus()
