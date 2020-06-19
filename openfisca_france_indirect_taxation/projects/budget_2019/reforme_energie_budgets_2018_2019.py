# -*- coding: utf-8 -*-

import numpy

from openfisca_core.reforms import Reform
from openfisca_france_indirect_taxation import FranceIndirectTaxationTaxBenefitSystem
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


def modify_parameters(parameters):
    node = ParameterNode(
        'officielle_2019_in_2017',
        data = {
            "description": "officielle_2019_in_2017",
            "diesel_2019_in_2017": {
                "description": "Surcroît de prix du diesel (en euros par hectolitres)",
                "unit": 'currency',
                "values": {'2016-01-01': 1 * 2.6 + 266 * (0.0446 - 0.0305)}  # 266 = valeur du contenu carbone du diesel (source : Ademe)
                },
            "essence_2019_in_2017": {
                "description": "Surcroît de prix de l'essence (en euros par hectolitres)",
                "unit": 'currency',
                "values": {'2016-01-01': 242 * (0.0446 - 0.0305)},
                },
            "combustibles_liquides_2019_in_2017": {
                "description": "Surcroît de prix du fioul domestique (en euros par litre)",
                "unit": 'currency',
                "values": {'2016-01-01': 3.24 * (0.0446 - 0.0305)},
                },
            "gaz_ville_2019_in_2017": {
                "description": "Surcroît de prix du gaz (en euros par kWh)",
                "unit": 'currency',
                "values": {'2016-01-01': 0.241 * (0.0446 - 0.0305)},
                },
            }
        )
    parameters.add_child('officielle_2019_in_2017', node)
    parameters.prestations.add_child('cheque_energie_reforme', FranceIndirectTaxationTaxBenefitSystem().parameters.prestations.cheque_energie)

    return parameters


class officielle_2019_in_2017(Reform):
    key = 'officielle_2019_in_2017',
    name = "Réforme de la fiscalité des énergies de 2018 par rapport aux taux de 2016",

    class cheques_energie(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Montant des chèques énergie tels que prévus par la loi"

        def formula(menage, period, parameters):
            revenu_fiscal = numpy.maximum(0.0, menage('revdecm', period) / 1.22)
            ocde10 = menage('ocde10', period)
            revenu_fiscal_uc = revenu_fiscal / ocde10
            bareme_cheque_energie_reforme = parameters(period).prestations.cheque_energie_reforme

            return numpy.select(
                [
                    (ocde10 == 1),
                    ((ocde10 > 1) * (ocde10 < 2)),
                    (ocde10 >= 2),
                    ],
                [
                    bareme_cheque_energie_reforme.menage_avec_1_uc.calc(revenu_fiscal_uc),
                    bareme_cheque_energie_reforme.menage_entre_1_et_2_uc.calc(revenu_fiscal_uc),
                    bareme_cheque_energie_reforme.menage_avec_2_uc_et_plus.calc(revenu_fiscal_uc),
                    ],
                default = 0.0
                )

    class combustibles_liquides_ticpe_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de TICPE sur le combustibles_liquides domestique après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

            accise_combustibles_liquides_ticpe = (
                parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.gazole_fioul_domestique_hectolitre / 100
                )
            reforme_combustibles_liquides = \
                parameters(period.start).officielle_2019_in_2017.combustibles_liquides_2019_in_2017
            accise_combustibles_liquides_ajustee = accise_combustibles_liquides_ticpe + reforme_combustibles_liquides
            prix_fioul_ttc = \
                parameters(period.start).tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre
            prix_fioul_ttc_ajuste = prix_fioul_ttc + reforme_combustibles_liquides

            taux_implicite_combustibles_liquides_ajuste = (
                (accise_combustibles_liquides_ajustee * (1 + taux_plein_tva))
                / (prix_fioul_ttc_ajuste - accise_combustibles_liquides_ajustee * (1 + taux_plein_tva))
                )

            depenses_combustibles_liquides_ajustees = menage('depenses_combustibles_liquides_officielle_2019_in_2017', period)
            depenses_combustibles_liquides_htva = \
                depenses_combustibles_liquides_ajustees - tax_from_expense_including_tax(depenses_combustibles_liquides_ajustees, taux_plein_tva)
            montant_combustibles_liquides_ticpe_ajuste = \
                tax_from_expense_including_tax(depenses_combustibles_liquides_htva, taux_implicite_combustibles_liquides_ajuste)

            return montant_combustibles_liquides_ticpe_ajuste

    class depenses_carburants_corrigees_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en carburants après réaction à la réforme"

        def formula(menage, period, parameters):
            depenses_diesel_ajustees = menage('depenses_diesel_corrigees_officielle_2019_in_2017', period)
            depenses_essence_ajustees = menage('depenses_essence_corrigees_officielle_2019_in_2017', period)
            depenses_carburants_ajustees = depenses_diesel_ajustees + depenses_essence_ajustees

            return depenses_carburants_ajustees

    class depenses_combustibles_liquides_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en combustibles_liquides après réaction à la réforme"

        def formula(menage, period, parameters):
            depenses_combustibles_liquides = menage('depenses_combustibles_liquides', period)
            prix_fioul_ttc = \
                parameters(period.start).tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre
            reforme_combustibles_liquides = \
                parameters(period.start).officielle_2019_in_2017.combustibles_liquides_2019_in_2017
            combustibles_liquides_elasticite_prix = menage('elas_price_2_2', period)
            depenses_combustibles_liquides_officielle_2019_in_2017 = \
                depenses_combustibles_liquides * (1 + (1 + combustibles_liquides_elasticite_prix) * reforme_combustibles_liquides / prix_fioul_ttc)

            return depenses_combustibles_liquides_officielle_2019_in_2017

    class depenses_diesel_corrigees_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en diesel après réaction à la réforme"

        def formula(menage, period, parameters):
            depenses_diesel = menage('depenses_diesel', period)
            diesel_ttc = parameters(period.start).prix_carburants.diesel_ttc
            reforme_diesel = parameters(period.start).officielle_2019_in_2017.diesel_2019_in_2017
            carburants_elasticite_prix = menage('elas_price_1_1', period)
            depenses_diesel_officielle_2019_in_2017 = \
                depenses_diesel * (1 + (1 + carburants_elasticite_prix) * reforme_diesel / diesel_ttc)

            return depenses_diesel_officielle_2019_in_2017

    class depenses_energies_logement_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en énergies dans le logement après la réforme"

        def formula(menage, period):
            depenses_electricite = menage('depenses_electricite', period)
            tarifs_sociaux_electricite = menage('tarifs_sociaux_electricite', period)
            depenses_gaz_ville_ajustees = menage('depenses_gaz_ville_officielle_2019_in_2017', period)
            depenses_gaz_liquefie = menage('depenses_gaz_liquefie', period)
            depenses_combustibles_liquides_ajustees = menage('depenses_combustibles_liquides_officielle_2019_in_2017', period)
            depenses_combustibles_solides = menage('depenses_combustibles_solides', period)
            depenses_energie_thermique = menage('depenses_energie_thermique', period)
            depenses_energies_logement_officielle_2019_in_2017 = (
                depenses_electricite + tarifs_sociaux_electricite + depenses_gaz_ville_ajustees + depenses_gaz_liquefie
                + depenses_combustibles_liquides_ajustees + depenses_combustibles_solides + depenses_energie_thermique
                )

            return depenses_energies_logement_officielle_2019_in_2017

    class depenses_essence_corrigees_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en essence après réaction à la réforme"

        def formula(menage, period, parameters):
            depenses_essence = menage('depenses_essence', period)
            super_95_ttc = parameters(period.start).prix_carburants.super_95_ttc
            reforme_essence = parameters(period.start).officielle_2019_in_2017.essence_2019_in_2017
            carburants_elasticite_prix = menage('elas_price_1_1', period)
            depenses_essence_officielle_2019_in_2017 = \
                depenses_essence * (1 + (1 + carburants_elasticite_prix) * reforme_essence / super_95_ttc)

            return depenses_essence_officielle_2019_in_2017

    class depenses_gaz_ville_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en gaz après réaction à la réforme"

        def formula(menage, period, parameters):
            depenses_gaz_variables = menage('depenses_gaz_variables', period)
            # Avec la réforme ces tarifs disparaissent, de nouvelles consommations entrent dans les dépenses des ménages :
            tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)
            depenses_gaz_variables = depenses_gaz_variables + tarifs_sociaux_gaz

            depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
            reforme_gaz = \
                parameters(period.start).officielle_2019_in_2017.gaz_ville_2019_in_2017
            gaz_elasticite_prix = menage('elas_price_2_2', period)
            depenses_gaz_variables = \
                depenses_gaz_variables * (1 + (1 + gaz_elasticite_prix) * reforme_gaz / depenses_gaz_prix_unitaire)
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
            depenses_gaz_ajustees = depenses_gaz_variables + depenses_gaz_tarif_fixe
            depenses_gaz_ajustees = numpy.array(depenses_gaz_ajustees, dtype = float)
            depenses_gaz_ajustees[numpy.isnan(depenses_gaz_ajustees)] = 0
            depenses_gaz_ajustees[numpy.isinf(depenses_gaz_ajustees)] = 0

            return depenses_gaz_ajustees

    class diesel_ticpe_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de TICPE sur le diesel après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

            # If the parameter does not have a defined value, it returns None
            majoration_ticpe_diesel = \
                parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_gazole.alsace

            accise_diesel = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.gazole

            accise_diesel_ticpe = (
                accise_diesel + majoration_ticpe_diesel
                if majoration_ticpe_diesel is not None
                else accise_diesel
                )

            reforme_diesel = parameters(period.start).officielle_2019_in_2017.diesel_2019_in_2017
            accise_diesel_ticpe_ajustee = accise_diesel_ticpe + reforme_diesel
            prix_diesel_ttc = parameters(period.start).prix_carburants.diesel_ttc
            prix_diesel_ttc_ajuste = prix_diesel_ttc + reforme_diesel
            taux_implicite_diesel_ajuste = (
                (accise_diesel_ticpe_ajustee * (1 + taux_plein_tva))
                / (prix_diesel_ttc_ajuste - accise_diesel_ticpe_ajustee * (1 + taux_plein_tva))
                )

            depenses_diesel_officielle_2019_in_2017 = \
                menage('depenses_diesel_corrigees_officielle_2019_in_2017', period)
            depenses_diesel_htva_ajustees = (
                depenses_diesel_officielle_2019_in_2017
                - tax_from_expense_including_tax(depenses_diesel_officielle_2019_in_2017, taux_plein_tva)
                )
            montant_diesel_ticpe_ajuste = (
                tax_from_expense_including_tax(depenses_diesel_htva_ajustees, taux_implicite_diesel_ajuste)
                )

            return montant_diesel_ticpe_ajuste

    class gains_tva_carburants_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes en TVA sur les carburants de la réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_carburants_corrigees_officielle_2019_in_2017 = \
                menage('depenses_carburants_corrigees_officielle_2019_in_2017', period)
            tva_depenses_carburants_corrigees_officielle_2019_in_2017 = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_carburants_corrigees_officielle_2019_in_2017
                )
            depenses_carburants_corrigees = \
                menage('depenses_carburants', period)
            tva_depenses_carburants_corrigees = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_carburants_corrigees
                )
            gains_tva_carburants = (
                tva_depenses_carburants_corrigees_officielle_2019_in_2017
                - tva_depenses_carburants_corrigees
                )
            return gains_tva_carburants

    class gains_tva_combustibles_liquides_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur les combustibles liquides"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_combustibles_liquides_officielle_2019_in_2017 = \
                menage('depenses_combustibles_liquides_officielle_2019_in_2017', period)
            tva_depenses_combustibles_liquides_officielle_2019_in_2017 = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_combustibles_liquides_officielle_2019_in_2017
                )
            depenses_combustibles_liquides = \
                menage('depenses_combustibles_liquides', period)
            tva_depenses_combustibles_liquides = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_combustibles_liquides
                )
            gains_tva_combustibles_liquides = (
                tva_depenses_combustibles_liquides_officielle_2019_in_2017
                - tva_depenses_combustibles_liquides
                )
            return gains_tva_combustibles_liquides

    class gains_tva_gaz_ville_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur le gaz naturel"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
            depenses_gaz_ville_officielle_2019_in_2017 = \
                menage('depenses_gaz_ville_officielle_2019_in_2017', period)
            tva_depenses_gaz_ville_officielle_2019_in_2017 = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * (depenses_gaz_ville_officielle_2019_in_2017 - depenses_gaz_tarif_fixe)
                )
            depenses_gaz_ville = \
                menage('depenses_gaz_ville', period)
            tva_depenses_gaz_ville = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * (depenses_gaz_ville - depenses_gaz_tarif_fixe)
                )
            gains_tva_gaz_ville = (
                tva_depenses_gaz_ville_officielle_2019_in_2017
                - tva_depenses_gaz_ville
                )
            return gains_tva_gaz_ville

    class gains_tva_total_energies_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur toutes les énergies"

        def formula(menage, period):
            gains_carburants = menage('gains_tva_carburants_officielle_2019_in_2017', period)
            gains_combustibles_liquides = menage('gains_tva_combustibles_liquides_officielle_2019_in_2017', period)
            gains_gaz_ville = menage('gains_tva_gaz_ville_officielle_2019_in_2017', period)

            somme_gains = gains_carburants + gains_combustibles_liquides + gains_gaz_ville
            return somme_gains

    class quantites_gaz_final_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Quantités de gaz consommées après la réforme"

        def formula(menage, period, parameters):
            depenses_gaz_ville_officielle_2019_in_2017 = menage('depenses_gaz_ville_officielle_2019_in_2017', period)
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
            depenses_gaz_variables = depenses_gaz_ville_officielle_2019_in_2017 - depenses_gaz_tarif_fixe

            depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
            reforme_gaz = \
                parameters(period.start).officielle_2019_in_2017.gaz_ville_2019_in_2017

            quantites_gaz_ajustees = depenses_gaz_variables / (depenses_gaz_prix_unitaire + reforme_gaz)

            return quantites_gaz_ajustees

    class revenu_reforme_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Revenu généré par la réforme officielle 2018 avant redistribution"

        def formula(menage, period):
            total_taxes_energies = menage('total_taxes_energies', period)
            total_taxes_energies_officielle_2019_in_2017 = \
                menage('total_taxes_energies_officielle_2019_in_2017', period)
            gains_tva_total_energies = menage('gains_tva_total_energies_officielle_2019_in_2017', period)
            tarifs_sociaux_electricite = menage('tarifs_sociaux_electricite', period)
            tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)

            revenu_reforme = (
                total_taxes_energies_officielle_2019_in_2017 - total_taxes_energies
                + gains_tva_total_energies + tarifs_sociaux_electricite + tarifs_sociaux_gaz
                )

            return revenu_reforme

    class sp_e10_ticpe_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de la TICPE sur le SP E10 après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

            accise_super_e10 = \
                parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_e10
            # If the parameter does not have a defined value, it returns None
            majoration_ticpe_super_e10 = \
                parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_super.alsace

            accise_ticpe_super_e10 = (
                accise_super_e10 + majoration_ticpe_super_e10
                if majoration_ticpe_super_e10 is not None
                else accise_super_e10
                )

            reforme_essence = parameters(period.start).officielle_2019_in_2017.essence_2019_in_2017
            accise_ticpe_super_e10_ajustee = accise_ticpe_super_e10 + reforme_essence
            super_95_e10_ttc = parameters(period.start).prix_carburants.super_95_e10_ttc
            super_95_e10_ttc_ajuste = super_95_e10_ttc + reforme_essence
            taux_implicite_sp_e10_ajuste = (
                (accise_ticpe_super_e10_ajustee * (1 + taux_plein_tva))
                / (super_95_e10_ttc_ajuste - accise_ticpe_super_e10_ajustee * (1 + taux_plein_tva))
                )
            depenses_essence_officielle_2019_in_2017 = \
                menage('depenses_essence_corrigees_officielle_2019_in_2017', period)
            part_sp_e10 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_e10
            sp_e10_depenses_ajustees = depenses_essence_officielle_2019_in_2017 * part_sp_e10
            sp_e10_depenses_htva_ajustees = \
                sp_e10_depenses_ajustees - tax_from_expense_including_tax(sp_e10_depenses_ajustees, taux_plein_tva)
            montant_sp_e10_ticpe_ajuste = \
                tax_from_expense_including_tax(sp_e10_depenses_htva_ajustees, taux_implicite_sp_e10_ajuste)

            return montant_sp_e10_ticpe_ajuste

    class sp95_ticpe_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de TICPE sur le sp_95 après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

            accise_super95 = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_95_98
            majoration_ticpe_super95 = \
                parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_super.alsace
            accise_ticpe_super95 = (
                accise_super95 + majoration_ticpe_super95
                if majoration_ticpe_super95 is not None
                else accise_super95
                )

            reforme_essence = parameters(period.start).officielle_2019_in_2017.essence_2019_in_2017
            accise_ticpe_super95_ajustee = accise_ticpe_super95 + reforme_essence
            super_95_ttc = parameters(period.start).prix_carburants.super_95_ttc
            super_95_ttc_ajuste = super_95_ttc + reforme_essence
            taux_implicite_sp95_ajuste = (
                (accise_ticpe_super95_ajustee * (1 + taux_plein_tva))
                / (super_95_ttc_ajuste - accise_ticpe_super95_ajustee * (1 + taux_plein_tva))
                )
            depenses_essence_officielle_2019_in_2017 = \
                menage('depenses_essence_corrigees_officielle_2019_in_2017', period)
            part_sp95 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_95
            depenses_sp_95_ajustees = depenses_essence_officielle_2019_in_2017 * part_sp95
            depenses_sp_95_htva_ajustees = (
                depenses_sp_95_ajustees - tax_from_expense_including_tax(depenses_sp_95_ajustees, taux_plein_tva)
                )
            montant_sp95_ticpe_ajuste = (
                tax_from_expense_including_tax(depenses_sp_95_htva_ajustees, taux_implicite_sp95_ajuste)
                )

            return montant_sp95_ticpe_ajuste

    class sp98_ticpe_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de TICPE sur le sp_98 après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

            accise_super98 = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_95_98
            majoration_ticpe_super98 = \
                parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_super.alsace
            accise_ticpe_super98 = (
                accise_super98 + majoration_ticpe_super98
                if majoration_ticpe_super98 is not None
                else accise_super98
                )

            reforme_essence = parameters(period.start).officielle_2019_in_2017.essence_2019_in_2017
            accise_ticpe_super98_ajustee = accise_ticpe_super98 + reforme_essence
            super_98_ttc = parameters(period.start).prix_carburants.super_98_ttc
            super_98_ttc_ajuste = super_98_ttc + reforme_essence
            taux_implicite_sp98_ajuste = (
                (accise_ticpe_super98_ajustee * (1 + taux_plein_tva))
                / (super_98_ttc_ajuste - accise_ticpe_super98_ajustee * (1 + taux_plein_tva))
                )
            depenses_essence_officielle_2019_in_2017 = \
                menage('depenses_essence_corrigees_officielle_2019_in_2017', period)
            part_sp98 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_98
            depenses_sp_98_ajustees = depenses_essence_officielle_2019_in_2017 * part_sp98
            depenses_sp_98_htva_ajustees = (
                depenses_sp_98_ajustees - tax_from_expense_including_tax(depenses_sp_98_ajustees, taux_plein_tva)
                )
            montant_sp98_ticpe_ajuste = (
                tax_from_expense_including_tax(depenses_sp_98_htva_ajustees, taux_implicite_sp98_ajuste)
                )

            return montant_sp98_ticpe_ajuste

    class super_plombe_ticpe_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de la TICPE sur le super plombé après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            accise_super_plombe_ticpe = \
                parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_plombe

            reforme_essence = parameters(period.start).officielle_2019_in_2017.essence_2019_in_2017
            accise_super_plombe_ticpe_ajustee = accise_super_plombe_ticpe + reforme_essence
            super_plombe_ttc = parameters(period.start).prix_carburants.super_plombe_ttc
            super_plombe_ttc_ajuste = super_plombe_ttc + reforme_essence
            taux_implicite_super_plombe_ajuste = (
                (accise_super_plombe_ticpe_ajustee * (1 + taux_plein_tva))
                / (super_plombe_ttc_ajuste - accise_super_plombe_ticpe_ajustee * (1 + taux_plein_tva))
                )
            depenses_essence_officielle_2019_in_2017 = \
                menage('depenses_essence_corrigees_officielle_2019_in_2017', period)
            part_super_plombe = \
                parameters(period.start).imposition_indirecte.part_type_supercarburants.super_plombe
            depenses_super_plombe_ajustees = depenses_essence_officielle_2019_in_2017 * part_super_plombe
            depenses_super_plombe_htva_ajustees = (
                depenses_super_plombe_ajustees
                - tax_from_expense_including_tax(depenses_super_plombe_ajustees, taux_plein_tva)
                )
            montant_super_plombe_ticpe_ajuste = \
                tax_from_expense_including_tax(depenses_super_plombe_htva_ajustees, taux_implicite_super_plombe_ajuste)

            return montant_super_plombe_ticpe_ajuste

    class taxe_gaz_ville_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la taxe sur la consommation de gaz - ceteris paribus"
        # On considère que les contributions sur les taxes précédentes ne sont pas affectées

        def formula(menage, period, parameters):
            quantites_gaz_ajustees = menage('quantites_gaz_final_officielle_2019_in_2017', period)
            reforme_gaz = parameters(period.start).officielle_2019_in_2017.gaz_ville_2019_in_2017
            recettes_gaz = quantites_gaz_ajustees * reforme_gaz

            return recettes_gaz

    class total_taxes_energies_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Différence entre les contributions aux taxes sur l'énergie après la hausse cce 2016-2018"

        def formula(menage, period):
            essence_ticpe = menage('essence_ticpe', period)
            diesel_ticpe = menage('diesel_ticpe', period)
            combustibles_liquides_ticpe = menage('combustibles_liquides_ticpe', period)
            taxe_gaz_ville = menage('taxe_gaz_ville_officielle_2019_in_2017', period)
            return diesel_ticpe + essence_ticpe + combustibles_liquides_ticpe + taxe_gaz_ville

    def apply(self):
        self.update_variable(self.cheques_energie)
        self.update_variable(self.combustibles_liquides_ticpe_officielle_2019_in_2017)
        self.update_variable(self.depenses_carburants_corrigees_officielle_2019_in_2017)
        self.update_variable(self.depenses_combustibles_liquides_officielle_2019_in_2017)
        self.update_variable(self.depenses_diesel_corrigees_officielle_2019_in_2017)
        self.update_variable(self.depenses_energies_logement_officielle_2019_in_2017)
        self.update_variable(self.depenses_essence_corrigees_officielle_2019_in_2017)
        self.update_variable(self.depenses_gaz_ville_officielle_2019_in_2017)
        self.update_variable(self.diesel_ticpe_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_carburants_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_combustibles_liquides_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_gaz_ville_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_total_energies_officielle_2019_in_2017)
        self.update_variable(self.quantites_gaz_final_officielle_2019_in_2017)
        self.update_variable(self.revenu_reforme_officielle_2019_in_2017)
        self.update_variable(self.sp_e10_ticpe_officielle_2019_in_2017)
        self.update_variable(self.sp95_ticpe_officielle_2019_in_2017)
        self.update_variable(self.sp98_ticpe_officielle_2019_in_2017)
        self.update_variable(self.super_plombe_ticpe_officielle_2019_in_2017)
        self.update_variable(self.taxe_gaz_ville_officielle_2019_in_2017)
        self.update_variable(self.total_taxes_energies_officielle_2019_in_2017)
        self.modify_parameters(modifier_function = modify_parameters)