# -*- coding: utf-8 -*-

# Dans ce script on crée deux fichiers .csv pour les deux bases de données
# homogènes, qui seront ensuite importées dans R pour l'appariement..


from __future__ import division

import os
import pkg_resources


from openfisca_france_indirect_taxation.build_survey_data.matching_erfs.step_2_homogenize_variables import \
    homogenize_definitions

assets_directory = os.path.join(
    pkg_resources.get_distribution('openfisca_france_indirect_taxation').location
    )


def create_donation_classes():
    for base in [0,1]:
        data = homogenize_definitions()[base]

        # Classes based on niveau_vie_decile and aides_logement
        data['donation_class_1'] = data['nactifs']
        data.loc[data['nactifs'] > 2, 'nactifs'] = 3
        
        if base == 0:
            data_erfs = data
        else:
            data_bdf = data
                
    return data_erfs, data_bdf
                
data = create_donation_classes()    
data_erfs = data[0]
data_bdf = data[1]

# Sauvegarde des données dans des fichiers .csv
data_erfs.to_csv(os.path.join(assets_directory, 'openfisca_france_indirect_taxation', 'assets',
    'matching', 'matching_erfs', 'data_matching_erfs.csv'), sep = ',')
data_bdf.to_csv(os.path.join(assets_directory, 'openfisca_france_indirect_taxation', 'assets',
    'matching', 'matching_erfs', 'data_matching_bdf.csv'), sep = ',')