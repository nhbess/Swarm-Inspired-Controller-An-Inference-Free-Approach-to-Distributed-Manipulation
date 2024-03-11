import json


class DH:
    def __init__(self):
        self.data = {}

    def add_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.data:
                if isinstance(self.data[key], list):
                    self.data[key].append(value)
                else:
                    self.data[key] = [self.data[key], value]
            else:
                self.data[key] = value

    def add_data_list(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key].append(value)
            else:
                self.data[key] = [value]



    def to_json(self):
        return json.dumps(self.data, indent=4)

    def save_json(self, filename):

        with open(f'test.json', 'w') as file:
            json.dump(self.data, file, indent=4)
