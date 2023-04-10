import functionality as func

class Artwork:
    def __init__(self, data):
        self.QID = data.name
        self.objectvalue = data['object.value']
        date = data['dates.value']
        if 'http' in date or date == '':
            self.dated = False
            self.date = 'Undated'
        else:
            date = date.split('-')
            self.date = int(date[0])
            self.dated = True
        self.creators = str(data['creators.value']).split(';')
        self.depictions = str(data['depictions.value']).split(';')
        self.images = str(data['images.value']).split(';')
        self.collection = str(data['collections.value']).split(';')
        self.genres = str(data['genres.value']).split(';')
        self.materials = str(data['materials.value']).split(';')
        self.types = str(data['types.value']).split(';')
        self.creationPlace = str(data['creationlocations.value']).split(';')
        self.hasimage = True
        if self.images == ['']:
            self.hasimage = False
            self.images = ['https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg']

    def list_info(self):
        name = func.query_label(self.QID)
        creators = func.query_list(self.creators)

        return {
            'creators': creators,
            'title': name,
            'date': str(self.date),
            'images': self.images,
            'data_source': self.objectvalue
        }

    def info(self):
        name = func.query_label(self.QID)
        creators = func.query_list(self.creators)
        materials = func.query_list(self.materials)
        collection = func.query_list(self.collection)
        return {
            'creators': creators,
            'title': name,
            'date': str(self.date),
            'images': self.images,
            'data_source': self.objectvalue,
            'materials': materials,
            'collection': collection
        }
