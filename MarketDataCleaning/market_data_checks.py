import csv
import os
import statistics
from collections import OrderedDict
import datetime

# constants
ISSUES_LIST = ('missing value', 'stale value', 'outlier')
Z_SCORE_UPPER_TRESHOLD = 1.0
Z_SCORE_LOWER_TRESHOLD = -2.20

base_path = "<path to files here>"
filename = "InterestRate_history_raw.csv"

path_to_file = os.path.join(base_path, filename)


def find_outliers(date_value_dict, lower_thresh=Z_SCORE_LOWER_TRESHOLD, upper_thresh=Z_SCORE_UPPER_TRESHOLD):

    result = []

    arithmetic_mean = statistics.mean(date_value_dict.values())
    standard_deviation_population = statistics.pstdev(date_value_dict.values())

    zscores = []

    for key, value in date_value_dict.items():
        zscore = (value - arithmetic_mean)/standard_deviation_population
        if zscore > upper_thresh or zscore < lower_thresh:
            result.append((key, value, ISSUES_LIST[2]))
        zscores.append({"Value": value, "Z-Score": zscore})

    return result


def replace_missing_values(date_value_dict, missing_values_issues):
    for date in missing_values_issues.keys():
        delta = 1
        len_date_value_dict = len(date_value_dict)

        while len_date_value_dict:
            this_date = datetime.datetime.strptime(date, '%d/%m/%Y')
            prev_date = this_date - datetime.timedelta(delta)
            prev_date_str = prev_date.strftime('%d/%m/%Y')

            if date_value_dict.get(prev_date_str):
                price = date_value_dict[prev_date_str]
                if price > 0:
                    date_value_dict[date] = price
                    break
            delta += 1
            len_date_value_dict -= 1

    return date_value_dict


def find_stale_values(date_value_dict):

    stale_values = {}
    dates_list = []
    result = []

    for key, value in date_value_dict.items():
        if value not in stale_values and value > 0.0:  # ignore outliers
            stale_values[value] = [key]
        elif value > 0.0:
            stale_values[value].append(key)

    for key, values in stale_values.items():
        if len(values) > 5:  # more than 5 days
            for item in values:
                dates_list.append(datetime.datetime.strptime(item, '%d/%m/%Y'))

            sorted_dates = sorted(dates_list)

            diffs_between_days = [(x - sorted_dates[i - 1]).days for i, x in enumerate(sorted_dates)][1:]
            num_days = len([x for x in diffs_between_days if x < 3])  # if we span a weekend
            if num_days > 5:
                for item in sorted_dates:
                    result.append((item.strftime('%d/%m/%Y'), key, ISSUES_LIST[1]))

    return result


def check_files_data(path_to_file):

    with open(path_to_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        date_value_dict = OrderedDict()
        total_issues = {}
        list_missing = []
        result = []

        for row in csv_reader:
            if line_count == 0:
                price_date, last_price, issue = row[0], row[1], 'Issue'
                line_count += 1
            else:
                # dealing with missing values here
                if row[1] is '':
                    date, last_price, issue = row[0], float('nan'), ISSUES_LIST[0]
                    list_missing.append((date, last_price, issue))
                    total_issues[date] = last_price, issue

                date_value_dict[row[0]] = float(row[1]) if row[1] is not '' else float(-1)

        result.extend(list_missing)

        list_stales = find_stale_values(date_value_dict)
        result.extend(list_stales)

        date_value_dict = replace_missing_values(date_value_dict, total_issues)

        list_outliers = find_outliers(date_value_dict)
        result.extend(list_outliers)

    return result

if __name__ == '__main__':
    check_files_data(path_to_file)
