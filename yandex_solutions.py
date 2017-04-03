from collections import Counter
import random


def first():
    template_string = 'Arrival'
    sorted_letters = Counter(template_string).most_common()
    spoiled_string = ''.join([item[0] * item[1]
                              for item in sorted_letters])
    print(spoiled_string)


def unfold_nested_list(input_list):
    for item in input_list:
        if type(item) is list:
            yield from unfold_nested_list(item)
        else:
            yield item


def handler_func():
    template_list = ["a", ["b", "c", ["d"], "e"], [1, 2, 3, 4, 5], 1, 2, [3, 4]]
    unfolded_list = [item for item in unfold_nested_list(template_list)]
    print(unfolded_list)


class MoviesLib(object):
    """ 
    Simple class for three function:
        1. append movie library
        2. delete from movie library
        3. get random film
    """
    movies_set = {}

    def __init__(self, *args):
        if args:
            self.movies_set = set(args)
        else:
            self.movies_set = set('Empty')

    def append(self, movie_name_string):
        """ vars: 'movie_name' string value """
        if type(movie_name_string) is str:
            self.movies_set.add(movie_name_string)
        else:
            raise Exception('Unexpected value. Input type is str')

    def remove_movie(self, movie_name_string):
        """ vars: 'movie_name' string value """
        if type(movie_name_string is str):
            self.movies_set.remove(movie_name_string)
        else:
            raise Exception('Unexpected value. Input type is str')

    def print_lib(self):
        print(self.movies_set)

    def get_randmovie(self):
        return random.sample(self.movies_set, 1)


def class_test():
    obj = MoviesLib('Sherlock', 'Fight Club', 'Fate/Zero')
    obj.append('La La Land')
    obj.remove_movie('Sherlock')
    obj.append('Ghost In The Shell')
    print(obj.get_randmovie())
    obj.print_lib()