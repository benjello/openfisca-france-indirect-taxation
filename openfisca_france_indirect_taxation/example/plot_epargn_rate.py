# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 16:22:22 2015

@author: thomas.douenne
"""

# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import division

from pandas import concat

from openfisca_france_indirect_taxation.example.utils_example import simulate_df, df_weighted_average_grouped, \
    graph_builder_line


if __name__ == '__main__':
    import logging
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)

    list_coicop12 = []
    for coicop12_index in range(1, 13):
        list_coicop12.append('coicop12_{}'.format(coicop12_index))

    var_to_be_simulated = [
        'niveau_vie_decile',
        'rev_disponible',
        'pondmen',
        'tva_total',
        'tipp',
        'taxe_assurance_sante',
        'droit_d_accise_vin',
        'droit_d_accise_cigares',
        'taxe_assurance_transport',
        'taxe_autres_assurances',
        'droit_d_accise_biere',
        'droit_d_accise_alcools_forts',
        'droit_d_accise_cigarette',
        'droit_d_accise_tabac_a_rouler',
        ]

    var_to_be_simulated += list_coicop12

    p = dict()
    df_to_graph = None
    for year in [2000, 2005, 2011]:
        simulation_data_frame = simulate_df(var_to_be_simulated = var_to_be_simulated, year = year)
        aggregates_data_frame = df_weighted_average_grouped(dataframe = simulation_data_frame,
            groupe = 'niveau_vie_decile', varlist = var_to_be_simulated)
        aggregates_data_frame['taxe_1'] = aggregates_data_frame['tva_total']
        aggregates_data_frame['taxe_2'] = aggregates_data_frame['tipp']
        aggregates_data_frame['taxe_3'] = (
            aggregates_data_frame['taxe_assurance_sante'] +
            aggregates_data_frame['taxe_assurance_transport'] +
            aggregates_data_frame['taxe_autres_assurances']
            )
        aggregates_data_frame['taxe_4'] = (
            aggregates_data_frame['droit_d_accise_vin'] +
            aggregates_data_frame['droit_d_accise_biere'] +
            aggregates_data_frame['droit_d_accise_alcools_forts']
            )
        aggregates_data_frame['taxe_5'] = (
            aggregates_data_frame['droit_d_accise_cigares'] +
            aggregates_data_frame['droit_d_accise_cigarette'] +
            aggregates_data_frame['droit_d_accise_tabac_a_rouler']
            )
        aggregates_data_frame['total'] = (
            aggregates_data_frame['taxe_{}'.format(1)] +
            aggregates_data_frame['taxe_{}'.format(2)] +
            aggregates_data_frame['taxe_{}'.format(3)] +
            aggregates_data_frame['taxe_{}'.format(4)] +
            aggregates_data_frame['taxe_{}'.format(5)]
            )
        aggregates_data_frame['{}'.format(year)] = \
            aggregates_data_frame['total'] / aggregates_data_frame['rev_disponible']

        p['{}'.format(year)] = aggregates_data_frame['{}'.format(year)]
        if df_to_graph is not None:
            df_to_graph = concat([df_to_graph, p['{}'.format(year)]], axis = 1)
        else:
            df_to_graph = p['{}'.format(year)]

    graph_builder_line(df_to_graph)
