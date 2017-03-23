#!/usr/bin/env python3
"""
    Info string
"""
import re
import json
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt


def convert_input_file(name_file):
    os.system('tshark -r ' + name_file + ' -t ad > out.txt')


def find_string(f):
    """ parse func find ip and mac"""
    # parse_list contain of dicts {'IP', 'MAC'}
    parse_list = []
    path_list = []
    for line in f:
        line = line.strip(' \n')
        if not line:
            continue
        if 'ARP' in line:
            ip = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line)
            mac = re.findall(r'(?:[0-9a-fA-F]:?){12}', line)
            if not mac:
                continue
            tmp_dict = {'IP': ip[0], 'MAC': mac[0]}
            parse_list.append(tmp_dict)
        else:
            path = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b.{3}\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line)
            if not path:
                continue
            else:
                numbers_list = path[0].split(' → ')
                if (numbers_list[0], numbers_list[1]) in path_list:
                    continue
                else:
                    path_list.append((numbers_list[0], numbers_list[1]))
    for i in parse_list:
        print(i['IP'], i['MAC'])
    for i in path_list:
        print(i)
    return parse_list, path_list


def main():
    """ opening and parsing """
    with open('out.txt', 'r') as f:
        parse_list, path_list = find_string(f)
        G = nx.MultiDiGraph()
        G.add_edges_from(path_list)
        nx.draw(G, with_labels=True)
        plt.show()


convert_input_file(sys.argv[1])
main()
