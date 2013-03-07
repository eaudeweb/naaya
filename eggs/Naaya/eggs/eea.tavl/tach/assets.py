from django_assets import Bundle, register


JS_ASSETS = (
    'js/main.js',
)


CSS_ASSETS = (
    'css/style.css',
)


js = Bundle(*JS_ASSETS, filters='jsmin', output='gen/packed.js')
css = Bundle(*CSS_ASSETS, filters='cssmin', output='gen/packed.css')


register('js', js)
register('css', css)