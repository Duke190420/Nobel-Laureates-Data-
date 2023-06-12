import numpy as np
import pandas as pd
import os
import requests
import sys
import matplotlib.pyplot as plt

if __name__ == '__main__':
    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if 'Nobel_laureates.json' not in os.listdir('../Data'):
        sys.stderr.write("[INFO] Dataset is loading.\n")
        url = "https://www.dropbox.com/s/m6ld4vaq2sz3ovd/nobel_laureates.json?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/Nobel_laureates.json', 'wb').write(r.content)
        sys.stderr.write("[INFO] Loaded.\n")
    # Load the data and reset the index
    data = pd.read_json("../Data/Nobel_laureates.json")
    data.dropna(axis=0, inplace=True, subset=['gender'])
    data.reset_index(drop=True, inplace=True)

    # Process the place_of_birth column
    data['place_of_birth'] = data['place_of_birth'].apply(
        lambda x: x.split(',')[-1].strip() if (x is not None and ',' in x) else None)

    data['born_in'].replace({'': None, 'unknown': None}, inplace=True)
    data['born_in'].fillna(data['place_of_birth'], inplace=True)

    # drop rows where 'born_in' is still None
    data.dropna(subset=['born_in'], inplace=True)

    # reset index
    data.reset_index(drop=True, inplace=True)

    data['born_in'].replace({'US': 'USA', 'United States': 'USA', 'U.S.': 'USA', 'United Kingdom': 'UK'}, inplace=True)

    data['year_born'] = data['date_of_birth'].apply(
        lambda x: None if x is None
        else x.split(' ')[-1] if ' ' in x and ',' not in x
        else x.split('-')[0] if '-' in x
        else x.split(',')[-1] if ',' in x
        else x)

    data['year_born'] = pd.to_numeric(data['year_born'], errors='coerce')  # convert to numeric, turn errors into NaN
    data['age_of_winning'] = data['year'] - data['year_born']
    colors = ['blue', 'orange', 'red', 'yellow', 'green', 'pink', 'brown', 'cyan', 'purple']
    # plt.figure(figsize=(12, 12))
    dummy = data['born_in'].value_counts()
    plot_data = dummy[dummy >= 25]
    plot_data['Other countries'] = dummy[dummy < 25].sum()
    plot_data.to_frame()
    plot_data = plot_data.sort_values(ascending=False)
    labels = plot_data.index
    plot_data = plot_data.values
    explode = [0.0, 0.0, 0.0, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]

    data['category'] = data['category'].replace(r'^\s*$', np.nan, regex=True)
    data['category'].dropna(inplace=True)
    count = data.groupby(['category', 'gender']).size().reset_index(name='counts')

    # Creating the label and corresponding value    plt.pie(plot_data,
    #             explode=explode,
    #             labels=labels,
    #             colors=colors,
    #             autopct=lambda p: f'{p:.2f}% \n {p*sum(plot_data)/100 :.0f}',
    #             )

    label = count['category'].value_counts().index
    male_count = count['counts'].iloc[1::2]
    female_count = count['counts'].iloc[::2]

    # Creating x-axis values depending on the label
    x_axis = np.arange(len(label))

    # Increasing fig size
    # plt.figure(figsize=(10, 10))
    # plt.bar(x_axis-0.2, male_count, width=0.4, label='Males', color='blue')
    # plt.bar(x_axis+0.2, female_count, width=0.4, label='Females', color='crimson')
    # set tick labels and their location
    # plt.xticks(x_axis, label)
    # plt.yticks(np.arange(0, 201, 25))
    # plt.xlabel('Category', fontsize=14)
    # plt.ylabel('Nobel Laureates Count', fontsize=14)
    # plt.title('The total count of male and female Nobel Prize winners by categories', fontsize=20)

    # plt.legend()

    # plt.show()

    plt.figure(figsize=(12, 9))
    age_category = data.groupby(['category', 'age_of_winning']).size().reset_index(name='counts')
    ac_label = age_category['category'].unique()
    age_lists = [data[data['category'] == category]['age_of_winning'].values for category in ac_label]
    age_lists.append(data['age_of_winning'].values)
    ac_label = np.append(ac_label, 'All categories')
    bp = plt.boxplot(age_lists, labels=ac_label, showmeans=True)

    plt.title('Distribution of ages by Category', fontsize=12)
    plt.ylabel('Age of obtaining the Nobel Prize', fontsize=10)

    plt.show()




