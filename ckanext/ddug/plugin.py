import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class DdugPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ddug')

    def after_map(self, m):
        m.connect('feedbackProv1', '/feedbackProv1', controller='ckanext.ddug.controller:DdugController', action='feedbackProv1')
        return m
