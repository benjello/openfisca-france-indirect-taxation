# -*- coding: utf-8 -*-

from __future__ import division

from openfisca_france_indirect_taxation.examples.utils_example import save_dataframe_to_graph
from openfisca_france_indirect_taxation.surveys import SurveyScenario
from openfisca_france_indirect_taxation.examples.calage_bdf_cn_energy import get_inflators_by_year_energy


inflators_by_year = get_inflators_by_year_energy(rebuild = False)

simulated_variables = [
    'rev_disp_loyerimput',
    'emissions_CO2_energies'
    ]

year = 2014
data_year = 2011
inflation_kwargs = dict(inflator_by_variable = inflators_by_year[year])
del inflation_kwargs['inflator_by_variable']['somme_coicop12']


survey_scenario = SurveyScenario.create(
    inflation_kwargs = inflation_kwargs,
    year = year,
    data_year = data_year
    )

df_by_entity = survey_scenario.create_data_frame_by_entity_key_plural(simulated_variables)
menages = df_by_entity['menages']

menages = menages.query('rev_disp_loyerimput > 1000')

menages['rank'] = menages['rev_disp_loyerimput'].argsort().argsort()
menages['quantile'] = menages['rank'] / len(menages)
del menages['rank']
menages['bin'] = 0
for i in range(0,50):
    menages['bin'] += \
        (menages['quantile'] < 0.02 * (i + 1)) * (menages['quantile'] > 0.02 * (i)) * 2 * (i + 1)

grouped = menages.groupby('bin')
dataframe = grouped.mean()

save_dataframe_to_graph(
    dataframe, 'Emissions/non_parametric_eec.csv'
    )
