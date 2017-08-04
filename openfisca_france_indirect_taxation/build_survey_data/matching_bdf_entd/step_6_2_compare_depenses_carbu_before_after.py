from __future__ import division

import os
import pkg_resources
import pandas as pd


default_config_files_directory = os.path.join(
    pkg_resources.get_distribution('openfisca_france_indirect_taxation').location
    )

data_matched = pd.read_csv(
    os.path.join(
        default_config_files_directory,
        'openfisca_france_indirect_taxation',
        'assets',
        'matching',
        'matching_entd',
        'data_matched_random.csv'
        ), sep =',', decimal = '.'
    )


    
def histogrammes(list_keys, list_values_bdf, list_values_entd):
    size_hist = np.arange(len(list_keys))
    plot_bdf = plt.bar(size_hist-0.125, list_values_bdf, color = 'b', align='center', width=0.25)
    plot_entd = plt.bar(size_hist+0.125, list_values_entd, color = 'r', align='center', width=0.25)
    plt.xticks(size_hist, list_keys)
    plt.legend((plot_bdf[0], plot_entd[0]), ('Matched', 'entd'))
    
    return plt

    
def histogram_depenses_annuelle_group(data_matched, group):
    list_values_poste_coicop = []
    list_values_depenses_carburants = []
    list_keys = []
    if group == 'niveau_vie_decile':
        min_element = 1
        max_element = 11
    if group == 'tuu':
        min_element = 0
        max_element = 9
    for element in range(min_element,max_element):
        data_matched_group = data_matched.query('{} == {}'.format(group, element))
        poste_coicop = (
            sum(data_matched_group['poste_coicop_722'] * data_matched_group['pondmen']) /
            data_matched_group['pondmen'].sum()
            )
        list_values_poste_coicop.append(poste_coicop)
    
        data_matched_group = data_matched.query('{} == {}'.format(group, element))
        depenses_carburants = (
            sum(data_matched_group['depenses_carburants'] * data_matched_group['pondmen']) /
            data_matched_group['pondmen'].sum()
            )

        list_values_depenses_carburants.append(depenses_carburants)
        list_keys.append('{}'.format(element))

    histogrammes(list_keys, list_values_poste_coicop, list_values_depenses_carburants)

    return plt

    
histogram_depenses_annuelle_group(data_matched_distance, 'niveau_vie_decile')
    