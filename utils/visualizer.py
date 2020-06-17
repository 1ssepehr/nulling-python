from math import log10
import matplotlib.pyplot as plt

def plot_data(data_x, res, isLog):
    """Plots the dataset data_x against [0:res:180].
    """

    for elem in data_x:
        if elem < 0:
            raise ValueError("negative values in list 'data_x'")
    
    data_y = [k * res for k in range(0, int(180 / res) + 1)] # res = 180/(N-1) where N = len(data_x)

    if len(data_x) != len(data_y): # size of each dataset must be N = 1 + (180/res)
        raise ValueError("resolution doesn't match with data_x's length")

    if isLog == True:
        data_x = list(map(lambda x: 10*log10(x), data_x))

    plt.plot(data_y, data_x)
    plt.show()
