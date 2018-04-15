import io
from functools import reduce
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
import numpy


class Dialog:
    def __init__(self, _id):
        self.id = _id
        self.queries = []
        self.num_of_unique_mods = 0


class Query:
    def __init__(self, time, text):
        self.time = time
        self.text = text


class Modifiers:
    def __init__(self):
        self.mods = {}
        self.true_count = 0

    def reset(self):
        self.true_count = 0
        for mod in self.mods:
            self.mods[mod] = False

    def mark(self, query_text):
        count = 0
        for mod in self.mods:
            if mod in query_text:
                count += 1
                if not self.mods[mod]:
                    self.mods[mod] = True
                    self.true_count += 1
        return count


class FileReader:
    def __init__(self, file, encoding):
        with io.open(file, encoding=encoding) as f:
            self.file = f.read()
            if self.file[-1] == '\n':
                self.file = self.file[:-1]

    def read_dialogs(self):
        dialogs = self.file.split('\n\n')
        dialog_list = []
        for dialog in dialogs:
            head, tail = dialog.split('>', maxsplit=1)
            d = Dialog(head)
            queries = tail.strip('\n').split('\n')
            for query in queries:
                time, query_text = query.split('\t')
                d.queries.append(Query(time, query_text))
            dialog_list.append(d)
        return len(dialog_list), dialog_list

    def read_modifiers(self):
        mods = Modifiers()
        mods.mods = {line: False for line in self.file.split('\n')}
        return mods


def check_dialog_modifiers(dialog, _modifiers, limit, graph_data):
    for query in dialog.queries[1:]:
        count = _modifiers.mark(query.text)
        if graph_data is not None:
            graph_data[query.time] += count
    dialog.num_of_unique_mods = _modifiers.true_count


def answer_1(dialogs, _modifiers, limit, graph_data=None):
    for dialog in dialogs:
        print("\r" + dialog.id, end='')
        _modifiers.reset()
        check_dialog_modifiers(dialog, _modifiers, limit, graph_data)
    print()


def over_limit(dialog, limit):
    if dialog.num_of_unique_mods >= limit:
        return 1
    else:
        return 0


def plot_and_save(graph_data, output_file):
    graph_data_list = [(k, graph_data[k]) for k in graph_data]
    values = [v[1] for v in sorted(graph_data_list)]
    dates = pd.date_range("00:00", "23:59", freq="1min").time
    series = pd.Series(values, index=dates)
    series.plot(figsize=(25, 25), xticks=pd.date_range("00:00", "23:59", freq="120min").time)
    plt.savefig(output_file)


if __name__ == "__main__":
    len_dialogs_1, dialogs_1 = FileReader('dialogy1.txt', 'utf-8').read_dialogs()
    len_dialogs_2, dialogs_2 = FileReader('dialogy2.txt', 'utf-8').read_dialogs()
    modifiers = FileReader('modifikatory.txt', 'cp1250').read_modifiers()

    queries_in_dialog_1 = [len(d.queries) for d in dialogs_1]
    queries_in_dialog_1.remove(max(queries_in_dialog_1))  # remove outlayer
    mean_dialogs_1 = numpy.mean(queries_in_dialog_1)
    median_dialogs_1 = numpy.median(queries_in_dialog_1)
    print("Dialogs 1 mean:", mean_dialogs_1)
    print("Dialogs 1 median:", median_dialogs_1)

    queries_in_dialog_2 = [len(d.queries) for d in dialogs_2]
    mean_dialogs_2 = numpy.mean(queries_in_dialog_2)
    median_dialogs_2 = numpy.median(queries_in_dialog_2)
    print("Dialogs 2 mean:", mean_dialogs_2)
    print("Dialogs 2 median:", median_dialogs_2)

    graph_data = defaultdict(lambda: 0)
    answer_1(dialogs_1, modifiers, 2, graph_data)
    plot_and_save(graph_data, 'output1.png')

    graph_data = defaultdict(lambda: 0)
    answer_1(dialogs_2, modifiers, 2, graph_data)
    plot_and_save(graph_data, 'output2.png')

    print("1a dialogs 1 length: {}".format(len_dialogs_1))
    print("1a dialogs 2 length: {}".format(len_dialogs_2))
    print("1b for dialogs 1: {}".format(reduce(lambda count, dialog: count + over_limit(dialog, 1), dialogs_1, 0)))
    print("1b for dialogs 2: {}".format(reduce(lambda count, dialog: count + over_limit(dialog, 1), dialogs_2, 0)))
    print("1c for dialogs 1: {}".format(reduce(lambda count, dialog: count + over_limit(dialog, 2), dialogs_1, 0)))
    print("1c for dialogs 2: {}".format(reduce(lambda count, dialog: count + over_limit(dialog, 2), dialogs_2, 0)))

