class TargetValueMapping:
    def __init__(self):
        self.No: int = 0
        self.Yes: int = 1

    def to_dict(self):
        return self.__dict__

    def reverse_mapping(self):
        mapping_response = self.to_dict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))