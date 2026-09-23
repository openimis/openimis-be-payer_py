from django.apps import AppConfig

from core.rights_declaration import RightsDeclaration

MODULE_NAME = "payer"


# Rights, by entity then by action. Same structure as `core.apps.DJANGO_PERMS`: the
# identifiers live in one place only, and the hierarchy makes sharing visible.
DJANGO_PERMS = {
    "payer": {
        "query": ("payer.view_payer", 121801),
        "create": ("payer.add_payer", 121802),
        # 121803 and not 122103: the latter belongs to medical
        # (gql_mutation_medical_items_update_perms) and the two were one and the same.
        "update": ("payer.change_payer", 121803),
        "delete": ("payer.delete_payer", 121804),
    },
}

_PERM_CFG = {
    "gql_query_payers_perms": ("payer", "query"),
    "gql_mutation_payer_add_perms": ("payer", "create"),
    "gql_mutation_payer_update_perms": ("payer", "update"),
    "gql_mutation_payer_delete_perms": ("payer", "delete"),
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


DEFAULT_CFG = {
    # 121803, not 122103: payer owns the 1218xx block (121801 search, 121802 add,
    # 121804 delete) and 121803 was the gap left for update. 122103 belongs to
    # medical (`gql_mutation_medical_items_update_perms`), so while payer update sat
    # on it the two were one right: granting either granted both.
}


class PayerConfig(AppConfig):
    name = MODULE_NAME

    # Rights: constants, no longer overridable. They go neither through DEFAULT_CFG
    # nor through ready(): `ModuleConfiguration.get_or_default` now ignores any
    # `_perms` key stored in the database.
    gql_query_payers_perms = RIGHTS.perms("payer", "query")
    gql_mutation_payer_add_perms = RIGHTS.perms("payer", "create")
    gql_mutation_payer_update_perms = RIGHTS.perms("payer", "update")
    gql_mutation_payer_delete_perms = RIGHTS.perms("payer", "delete")

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(PayerConfig, field):
                setattr(PayerConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)
