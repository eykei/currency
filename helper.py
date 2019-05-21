import requests, datetime, time, win32api
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal

#pip install pywin32

screenWidth = win32api.GetSystemMetrics(0)
screenHeight = win32api.GetSystemMetrics(1)

def generateData(apiKey, numDataPoints, startingPoint):
    #generate timepoints (plot's x axis)
    current_unix_time = time.time()  # seconds from unix epoch
    start_unix_time = current_unix_time - (startingPoint*24*60*60)
    unix_time_points = np.linspace(start_unix_time, current_unix_time, numDataPoints)
    time_points = [datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d') for x in unix_time_points]  # convert to YYYY-MM-DD format
    time_points = np.array(time_points)

    # download currency data, format: {'symbol': 'name'}
    url = f"http://apilayer.net/api/list?access_key={apiKey}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    currencies = data['currencies']

    # manage exclusions
    with open("exclusions.txt") as f:
        excludedCurrencies = f.readlines()
    excludedCurrencies = map(lambda x: x.rstrip('\n'), excludedCurrencies)
    for excluded in excludedCurrencies:
        if excluded in currencies.keys():
            del currencies[excluded]
    currencyCodes = list(currencies.keys())
    numCurrencies = len(currencyCodes)

    # download exchange rate data, generate exchange matrix
    exchange_matrix = np.zeros((numCurrencies, numDataPoints))
    for i in range(numDataPoints):
        url = f"http://apilayer.net/api/historical&date={time_points[i]}?access_key={apiKey}&currencies={','.join(currencyCodes)}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        exchangeRates = np.array(list(data['quotes'].values()))
        exchange_matrix[:, i] = exchangeRates  # fill matrix one column at a time

    # handle outliers - generate a boolean matrix of indices of values that are not outliers
    # nonoutlier_indices = np.ones((numCurrencies, numDataPoints))  # for testing without outlier rejection
    nonoutlier_indices = np.zeros((numCurrencies, numDataPoints))
    for i in range(numCurrencies):
        e = exchange_matrix[i]
        nonoutlier_indices[i] = abs(e - np.median(e)) <= 3 * np.std(e)  # Boolean matrix (if condition satisfied)
    nonoutlier_indices = nonoutlier_indices.astype(bool)

    # perform linear regression on each currency plot, and record the normalized slopes
    normalized_slopes = np.zeros(numCurrencies)
    coefficients = np.zeros((numCurrencies, 2))
    for i in range(numCurrencies):
        z = nonoutlier_indices[i]
        e = exchange_matrix[i, z]
        c = np.polyfit(np.arange(len(time_points[z])), e / np.median(e), 1)  #normalized slope
        normalized_slopes[i] = c[0]

        #find the coefficients of the linear equation
        c1 = np.polyfit(np.arange(len(time_points[z])), e, 1)
        coefficients[i] = [c1[0], c1[1]]



    return time_points, currencies, exchange_matrix, nonoutlier_indices, normalized_slopes, coefficients


def generatePlot(time_points, currencies, exchange_matrix, nonoutlier_indices, normalized_slopes, coefficients, k=-1):
    #generate a 2 x 3 plot and size it relative to the screen size
    fig, axs = plt.subplots(2, 3, figsize=(int(screenWidth/100), int(screenHeight/100)-1), constrained_layout=True)
    plt.suptitle('Cheap Places to Travel')
    normalized_slopes_argsort = np.argsort(normalized_slopes)

    for i in range(2):
        for j in range(3):
            current_index = normalized_slopes_argsort[k]
            z = nonoutlier_indices[current_index]

            x = np.arange(len(time_points[z]))
            y = coefficients[current_index][0] * x + coefficients[current_index][1]

            axs[i, j].plot(time_points[z], y, '--')  # plot the fitted line
            axs[i, j].plot(time_points[z], exchange_matrix[current_index, z])  #plot the exchange rate data
            axs[i, j].set_title(f"{-k}. {list(currencies.values())[current_index]} ({list(currencies.keys())[current_index]})")

            first_value = round(exchange_matrix[current_index, 0], 2)
            last_value = round(exchange_matrix[current_index, -1], 2)
            axs[i, j].text(0.7, 0.02, f'change: {int(((last_value-first_value)/first_value)*100)}%', transform=axs[i, j].transAxes)
            axs[i, j].text(0.7, 0.07, f'end: {last_value}', transform=axs[i, j].transAxes)
            axs[i, j].text(0.7, 0.12, f'start: {first_value}', transform=axs[i, j].transAxes)


            axs[i, j].xaxis.set_major_locator(plt.MaxNLocator(5))  # Limit plot to 5 xticks
            for tick in axs[i, j].get_xticklabels():
                tick.set_rotation(20)
            k -= 1

    return fig


'''
app.exchange_matrix[list(app.currencies.keys()).index('UZS'), :]
'''