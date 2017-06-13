# Dia

This is a experimental project currently in __intense development state__.

The entry point of the application is _dia.core.diacore_ instance.

For example: _from dia.core import diacore_

Previously it needs to be configured in the _dia.settings_ module.

It has:

* For adding new elements:

  * diacore.add_glucose_level(glucose)
  * diacore.add_activity(activity)
  * diacore.add_feeding(feeding)
  * diacore.add_insulin_administration(insulin)
  * diacore.update_trait(trait)

* For queries:

  * diacore.get_glucoses(user_pk, from_utc_timestamp=None, until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None, limit=None, order_by_utc_timestamp=True, order_ascending=True)
  * diacore.get_activities(self, user_pk, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True)
  * diacore.get_traits(user_pk, trait, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True)
  * diacore.get_feedings(user_pk, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True)
  * diacore.get_insulin_administrations(user_pk=None, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True)

* For recommendations:
	
  * diacore.get_recommendation(user_pk=None, utc_timestamp=None, predictive_system_unique_identificator=None)
  * diacore.all_predictive_systems
