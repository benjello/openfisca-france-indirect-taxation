from openfisca_core.reforms import Reform


from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


parameters_path = os.path.join(os.path.dirname(__file__), 'parameters')


def modify_parameters(parameters):
    reference = parameters.prix_carburants.diesel_ttc.clone()
    parameters.prix_carburants.add_child("diesel_ttc_reference", reference)
    reference_value = parameters.prix_carburants.diesel_ttc_reference(2014)
    parameters.prix_carburants.diesel_ttc.update(
        period = '2014',
        value = reference_value + 10
        )
    return parameters


class reforme_energie_test(Reform):
    key = 'reforme_energie_test'
    name = "Reforme test de l'imposition indirecte des carburants"

    def apply(self):
        self.modify_parameters(modifier_function = modify_parameters)
