# -*- coding: utf-8 -*-


from __future__ import division


from ..base import *  # noqa analysis:ignore


class elas_exp_1(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité dépense carburants"


class elas_exp_2(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité dépense énergie logement"


class elas_exp_3(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité dépense alimentaire"


class elas_exp_4(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité dépense autres biens non durables"


class elas_price_1_1(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix carburants"


class elas_price_1_2(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée carburants - énergie logement"


class elas_price_1_3(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée carburants - alimentaire"


class elas_price_1_4(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée carburants - autres biens non durables"


class elas_price_2_1(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée énergie logement - carburants"


class elas_price_2_2(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix énergie logement"


class elas_price_2_3(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée énergie logement - alimentaire"


class elas_price_2_4(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée énergie logement - autres biens non durables"


class elas_price_3_1(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée alimentaire - carburants"


class elas_price_3_2(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée énergie logement - alimentaire"


class elas_price_3_3(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix énergie logement"


class elas_price_3_4(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée énergie logement - autres biens non durables"


class elas_price_4_1(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée autres biens non durables - carburants"


class elas_price_4_2(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée autres biens non durables - énergie logement"


class elas_price_4_3(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix croisée autres biens non durables - alimentaire"


class elas_price_4_4(Variable):
    column = FloatCol(default = 0)
    entity_class = Menages
    label = u"Elasticité prix autres biens non durables"
