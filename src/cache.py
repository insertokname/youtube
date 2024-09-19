import pickle

class Cache:
    def __init__(self, cache_name: str) -> None:
        self.__cache_filename = cache_name
        try:
            with open(self.__cache_filename, 'rb') as file:
                self.__cache = pickle.load(file)
        except FileNotFoundError:
            # If file doesn't exist, create it with an empty array
            self.__cache = []  
            with open(self.__cache_filename, 'wb') as file:
                pickle.dump(self.__cache, file)

    # returns all the strings not found in the cache
    def find_new_strings(self, new_data: list[str]):
        out_data = []
        for data in new_data:
            if data not in self.__cache:
                out_data.append(data)
        out_data = list(dict.fromkeys(out_data))
        return out_data

    def update_cache(self, new_data: list[str]) -> None:
        self.__cache.extend(new_data)
        # remove all duplicate elements
        self.__cache = list(dict.fromkeys(self.__cache))
        with open(self.__cache_filename, 'wb') as file:
            pickle.dump(self.__cache, file)

    def delete_cache(self)->None:
        self.__cache = []
        with open(self.__cache_filename, 'wb') as file:
            pickle.dump(self.__cache, file)