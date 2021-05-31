class MyClass:
    def __init__(self):
        self.array = []
        self.avail_maps = []
        self.num_maps = 0
        self.map_name = []
        self.weight = 0
    def maps(self, i):
        if i >= 1:
            self.maps(i // 2)
            self.array.append(i % 2)
        m = []
        for j in range(7 - len(self.array)):
            m.append(0)
        for k in self.array:
            m.append(k)
        return m

    def maps_left(self, array):
        for i in array:
            if i:
                self.num_maps = self.num_maps + 1
        return self.num_maps

    def maps_names(self, i):
        array = self.maps(i)
        if array[0]:
            self.map_name.append('train')
        if array[1]:
            self.map_name.append('vertigo')
        if array[2]:
            self.map_name.append('nuke')
        if array[3]:
            self.map_name.append('overpass')
        if array[4]:
            self.map_name.append('dust2')
        if array[5]:
            self.map_name.append('inferno')
        if array[6]:
            self.map_name.append('mirage')
        return self.map_name

    def weight_of_map(self, name):
        if name == 'mirage':
            self.weight = 1
        if name == 'inferno':
            self.weight = 2
        if name == 'dust2':
            self.weight = 4
        if name == 'overpass':
            self.weight = 8
        if name == 'nuke':
            self.weight = 16
        if name == 'vertigo':
            self.weight = 32
        if name == 'train':
            self.weight = 64
        return self.weight
