# -*- coding: utf-8 -*-


from __future__ import division

from datetime import date
import logging

from biryani.strings import slugify




from openfisca_france_indirect_taxation.model.base import *


log = logging.getLogger(__name__)


categories_fiscales_data_frame = None
codes_coicop_data_frame = None


def generate_variables(tax_benefit_system, categories_fiscales = None, reform_key = None):
    assert categories_fiscales is not None
    reference_categories = sorted(categories_fiscales_data_frame['categorie_fiscale'].drop_duplicates())
    removed_categories = set()
    completed_categories_fiscales = insert_tva(categories_fiscales)

    if reform_key:
        reference_categories = set(reference_categories).union(set(categories_fiscales.categorie_fiscale.unique()))

    for categorie_fiscale in reference_categories:
        year_start = 1994
        year_final_stop = 2014
        functions_by_name = dict()
        for year in range(year_start, year_final_stop + 1):
            postes_coicop = sorted(
                completed_categories_fiscales.query(
                    'start <= @year and stop >= @year and categorie_fiscale == @categorie_fiscale'
                    )['code_coicop'].astype(str))

            if year == year_start:
                previous_postes_coicop = postes_coicop
                continue

            if previous_postes_coicop == postes_coicop and year != year_final_stop:
                continue
            else:
                year_stop = year - 1 if year != year_final_stop else year_final_stop

                dated_func = depenses_ht_categorie_function_creator(
                    previous_postes_coicop,
                    year_start = year_start,
                    year_stop = year_stop,
                    )
                dated_function_name = u"function_{year_start}_{year_stop}".format(
                    year_start = year_start, year_stop = year_stop)
                log.info(u'Creating fiscal category {} ({}-{}) with the following products {}'.format(
                    categorie_fiscale, year_start, year_stop, previous_postes_coicop))

                functions_by_name[dated_function_name] = dated_func

                year_start = year

            previous_postes_coicop = postes_coicop

        class_name = u'depenses_ht_{}'.format(categorie_fiscale)

        # Trick to create a class with a dynamic name.
        if reform_key is None:
            definitions_by_name = dict(
                column = FloatCol,
                entity = Menage,
                label = u"Dépenses hors taxes: {0}".format(categorie_fiscale),
                )
            definitions_by_name.update(functions_by_name)
            tax_benefit_system.add_variable(
                type(class_name.encode('utf-8'), (Variable,), definitions_by_name)
                )

        else:
            if class_name.encode('utf-8') in tax_benefit_system.column_by_name:
                definitions_by_name = dict()
                definitions_by_name.update(functions_by_name)
                tax_benefit_system.update_variable(
                    type(class_name.encode('utf-8'), (Variable,), definitions_by_name)
                    )
            else:
                definitions_by_name = dict(
                    column = FloatCol,
                    entity = Menage,
                    label = u"Dépenses hors taxes: {0}".format(categorie_fiscale),
                    )
                definitions_by_name.update(functions_by_name)
                tax_benefit_system.add_variable(
                    type(class_name.encode('utf-8'), (Variable,), definitions_by_name)
                    )

        del definitions_by_name


def preload_categories_fiscales_data_frame(tax_benefit_system):
    global codes_coicop_data_frame
    global categories_fiscales_data_frame
    if codes_coicop_data_frame is None or categories_fiscales_data_frame is None:
        categories_fiscales_data_frame, codes_coicop_data_frame = get_legislation_data_frames()

    generate_variables(tax_benefit_system, categories_fiscales = categories_fiscales_data_frame.copy())
