def zigzag_indicator(price_list, pips = 0.01, ext_depth = 12, ext_deviation = 0, ext_backstep = 2):
    len_price = len(price_list)
    extrema = [0] * len_price
    extrema_indexes = []
    last_highest = price_list[ext_depth]
    last_lowest = price_list[ext_depth]
    last_highest_index = ext_depth
    last_lowest_index = ext_depth
    last_extrema_type = None  # "high" or "low"
    i = ext_depth
    while i < len_price:
        if price_list[i] > last_highest + ext_deviation * pips:
            last_highest = price_list[i]
            last_highest_index = i
            if last_extrema_type == "low":
                extrema[last_lowest_index] = -1
                extrema_indexes.append(last_lowest_index)
            last_extrema_type = "high"
        elif price_list[i] < last_lowest - ext_deviation * pips:
            last_lowest = price_list[i]
            last_lowest_index = i
            if last_extrema_type == "high":
                extrema[last_highest_index] = 1
                extrema_indexes.append(last_highest_index)
            last_extrema_type = "low"
        else:
            if price_list[i] > last_highest:
                last_highest = price_list[i]
                last_highest_index = i
            if price_list[i] < last_lowest:
                last_lowest = price_list[i]
                last_lowest_index = i

        if last_extrema_type == "high" and price_list[i] < last_highest - ext_deviation * pips:
            last_lowest = price_list[i]
            last_lowest_index = i
            i = i - ext_backstep if i - ext_backstep > last_lowest_index else last_lowest_index
        elif last_extrema_type == "low" and price_list[i] > last_lowest + ext_deviation * pips:
            last_highest = price_list[i]
            last_highest_index = i
            i = i - ext_backstep if i - ext_backstep > last_highest_index else last_highest_index

        i += 1

    if last_extrema_type == "high":
        extrema[last_highest_index] = 1
        extrema_indexes.append(last_highest_index)
    elif last_extrema_type == "low":
        extrema[last_lowest_index] = -1
        extrema_indexes.append(last_lowest_index)

    return extrema, extrema_indexes



price_list = [
    100, 98, 97, 102, 110, 95, 100, 130, 140, 150,
    155, 135, 120, 110, 100, 120, 130, 115, 110, 90,
    80, 65, 100, 120, 130, 115, 110, 90, 85 ,120,
    100, 98, 97, 102, 110, 95, 100, 130, 140, 150,
    155, 135, 120, 110, 100, 120, 130, 115, 110, 90,
    95, 105, 115, 120, 130, 140, 155, 165, 170, 180,
    195, 200, 210, 160, 150, 140, 130, 115, 110, 90,
    ]

import matplotlib.pyplot as plt

def plot_zigzag(price_list, extrema):
    plt.figure(figsize=(12, 6))
    plt.plot(price_list, '-k', label='Price')

    for i in range(len(price_list)):
        if extrema[i] == 1:  # 高点
            plt.plot(i, price_list[i], 'go')
        elif extrema[i] == -1:  # 低点
            plt.plot(i, price_list[i], 'ro')

    plt.title('Zigzag Indicator')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

extrema, _ = zigzag_indicator(price_list)

print(zigzag_indicator(price_list))
plot_zigzag(price_list, extrema)

