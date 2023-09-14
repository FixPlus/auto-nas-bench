#!/usr/bin/env python3
import argparse
import csv
import matplotlib.pyplot as plt

class ResultEntry:
    def __init__(self):
       self.xAxis = []
       self.times = []
    def addPoint(self,res):
       self.xAxis.append(int(res[0]))
       self.stTimes.append(float(res[2]))

def split_by_benches(results):
    bench_names = set(())
    split_res = {}
    for res in results:
        bench_names.add(res[1])
    for name in bench_names:
        split_res[name] = {}
        bench_results = split_res[name]
        for res in filter(lambda x: x[1]==name, results):
            if res[0] not in bench_results:
                bench_results[res[0]] = [[], []]
            bench_results[res[0]][0].append(int(res[2]))
            bench_results[res[0]][1].append(float(res[3]))
    return split_res

def plot_res(results):
    index = 1
    for name, configs in results.items():
        plt.subplot(1, len(results), index)
        index += 1
        bar_width = 0.8 / len(configs)
        bar_offset = 0
        for confn, values in configs.items():
          ref_val = values[1][0]
          plt.bar([ x + bar_offset for x in values[0]], [min(x / ref_val, 1.0) for x in values[1]], width=bar_width, label=confn)
          bar_offset += bar_width
        plt.xlabel('thread num')
        plt.ylabel('time (normalized)')
        plt.title(name)
        plt.grid(which='both', axis='y')
        plt.minorticks_on()
        plt.legend(loc='upper center')
    plt.show()

parser = argparse.ArgumentParser(prog='plot_results.py', description='plot results of NAS benchmark')
parser.add_argument('results')
args = parser.parse_args()

with open(args.results) as resultfile:
    result_data = csv.reader(resultfile, delimiter=';')
    result_list = []
    for row in result_data:
        result_list.append(row)
    per_bench_results = split_by_benches(result_list)
    plot_res(per_bench_results)
