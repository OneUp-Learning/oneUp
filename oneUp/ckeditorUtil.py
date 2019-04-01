from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from ckeditor.widgets import LazyEncoder
from django.urls import reverse

DEFAULT_CONFIG = {
    'skin': 'moono-lisa',
    'toolbar_Basic': [
        ['Source', '-', 'Bold', 'Italic']
    ],
    'toolbar_Full': [
        ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
        ['Link', 'Unlink', 'Anchor'],
        ['Image', 'Flash', 'Table', 'HorizontalRule'],
        ['TextColor', 'BGColor'],
        ['Smiley', 'SpecialChar'], ['Source'],
    ],
    'toolbar': 'Full',
    'height': 291,
    'width': 835,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 725,
}

def config_ck_editor(value='', config_name='default', extra_plugins=None, external_plugin_resources=None):

    json_encode = LazyEncoder().encode

    config = DEFAULT_CONFIG.copy()
    # Try to get valid config from settings.
    configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
    if configs:
        if isinstance(configs, dict):
            # Make sure the config_name exists.
            if config_name in configs:
                con = configs[config_name]
                # Make sure the configuration is a dictionary.
                if not isinstance(con, dict):
                    raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] \
                            setting must be a dictionary type.' %
                                                config_name)
                # Override defaults with settings config.
                config.update(con)
            else:
                raise ImproperlyConfigured("No configuration named '%s' \
                        found in your CKEDITOR_CONFIGS setting." %
                                            config_name)
        else:
            raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a\
                    dictionary type.')
    extra_plugins = extra_plugins or []

    if extra_plugins:
        config['extraPlugins'] = ','.join(extra_plugins)

    external_plugin_resources = external_plugin_resources or []
    external_plugin_resources = [[force_text(a), force_text(b), force_text(c)]
                                     for a, b, c in external_plugin_resources]

    if 'filebrowserUploadUrl' not in config:
        config.setdefault('filebrowserUploadUrl', reverse('ckeditor_upload'))
    if 'filebrowserBrowseUrl' not in config:
        config.setdefault('filebrowserBrowseUrl', reverse('ckeditor_browse'))

    lang = get_language()
    if lang == 'zh-hans':
        lang = 'zh-cn'
    elif lang == 'zh-hant':
        lang = 'zh'
    config['language'] = lang

    return {'value': conditional_escape(force_text(value)),
            'config': json_encode(config),
            'external_plugin_resources': json_encode(external_plugin_resources)
            }
