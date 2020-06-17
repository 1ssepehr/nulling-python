from math import log10

def plot_data(data_x, res, isLog):
    """Plots the dataset data_x against [0:res:180].
    """

    for elem in data_x:
        if elem < 0:
            raise ValueError("negative values in list 'data_x'")
    
    data_y = [x for x in range(0, 180 + res, res)]

    if len(data_x) != len(data_y):
        raise ValueError("resolution doesn't match with data_x's length")

    if isLog == True:
        data_x = list(map(lambda x: 10*log10(x), data_x))

    # pass data_x and data_y to plotter

    pass