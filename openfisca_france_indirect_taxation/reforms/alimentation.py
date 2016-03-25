# -*- coding: utf-8 -*-

from __future__ import division


from numpy import logical_not as not_, minimum as min_
from openfisca_core import columns, reforms

from openfisca_france_indirect_taxation.model.consommation.categories_fiscales import generate_variables


def build_reform(tax_benefit_system):
    Reform = reforms.make_reform(
        key = 'reforme_alimentation',
        name = u"Réforme de l'imposition indirecte des biens alimentaires",
        reference = tax_benefit_system,
        )
    from openfisca_france_indirect_taxation.model.consommation.categories_fiscales import categories_fiscales_data_frame
    print categories_fiscales_data_frame.query("categorie_fiscale == 'tva_taux_super_reduit'")
    print categories_fiscales_data_frame.query("categorie_fiscale == 'vin'")
    categories_fiscales = categories_fiscales_data_frame.copy()
    categories_fiscales.loc[
        (categories_fiscales.categorie_fiscale == 'tva_taux_super_reduit') & (
            categories_fiscales.code_bdf.str.startswith('c06111')),
        'categorie_fiscale'
        ] = ''
    categories_fiscales.loc[
        categories_fiscales.categorie_fiscale == 'vin',
        'categorie_fiscale'
        ] = ''
    print categories_fiscales.query("categorie_fiscale == 'tva_taux_super_reduit'")
    print categories_fiscales.query("categorie_fiscale == 'vin'")

    generate_variables(
        categories_fiscales = categories_fiscales,
        Reform = Reform,
        tax_benefit_system = tax_benefit_system,
        )

    reform = Reform()
    # reform.modify_legislation_json(modifier_function = modify_legislation_json)
    return reform


# def modify_legislation_json(reference_legislation_json_copy):
#     reform_legislation_subtree = {
#         "@type": "Node",
#         "description": "Charge de loyer",
#         "children": {
#             "active": {
#                 "@type": "Parameter",
#                 "description": u"Activation de la charge",
#                 "format": "boolean",
#                 "values": [{'start': u'2002-01-01', 'stop': '2013-12-31', 'value': 1}],
#                 },
#             "plaf": {
#                 "@type": "Parameter",
#                 "description": u'Plafond mensuel',
#                 "format": 'integer',
#                 "unit": 'currency',
#                 "values": [{'start': '2002-01-01', 'stop': '2013-12-31', 'value': 1000}],
#                 },
#             "plaf_nbp": {
#                 "@type": "Parameter",
#                 "description": u'Ajuster le plafond au nombre de part',
#                 "format": 'boolean',
#                 "values": [{'start': '2002-01-01', 'stop': '2013-12-31', 'value': 0}],
#                 },
#             },
#         }
#     reference_legislation_json_copy['children']['charge_loyer'] = reform_legislation_subtree
#     return reference_legislation_json_copy
