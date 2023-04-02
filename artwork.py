from wikidata.client import Client

class Artwork:
    def __init__(self, data):
        self.QID = data.name
        self.objectvalue = data['object.value']
        date = data['dates.value']
        date = date.split('-')
        self.date = int(date[0])
        self.creators = str(data['creators.value']).split(';')
        self.depictions = str(data['depictions.value']).split(';')
        self.images = str(data['images.value']).split(';')
        self.collection = str(data['collection.value']).split(';')
        self.genres = str(data['genres.value']).split(';')
        self.materials = str(data['materials.value']).split(';')
        self.types = str(data['types.value']).split(';')
        self.creationPlace = str(data['creationPlace.value']).split(';')

        if len(self.images) < 1:
            self.images = ['https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg']

    def get_english(self):
        client = Client()
        materials_eng = []
        entity = client.get(self.QID, load=True)
        name = entity.label
        try:
            if isinstance(self.materials, list):
                for mat in self.materials:
                    entity = client.get(self.filter_QID(mat), load=True)
                    materials_eng.append(entity.label)
        except:
            materials_eng.append('No data')
        institute = []
        try:
            if isinstance(self.collection, list):
                for col in self.collection:
                    entity = client.get(self.filter_QID(col), load=True)
                    institute.append(entity.label)
        except:
            institute.append('No data')
        creators = []
        try:
            if isinstance(self.creators, list):
                for cre in self.creators:
                    entity = client.get(self.filter_QID(cre))
                    creators.append(entity.label)
        except:
            creators.append('No data')
        return name, materials_eng, institute, creators


    def filter_QID(self, string):
        string = string.split('/')
        return string[4]