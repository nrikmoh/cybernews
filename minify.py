# minify.py
# Minifies CSS and JS files for production
# Run before deployment: python minify.py

import os
import rjsmin
import rcssmin

def minify_file(input_path, output_path, minifier, file_type):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    minified = minifier(content)

    original_size = len(content)
    minified_size = len(minified)
    savings = (1 - minified_size / original_size) * 100

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(minified)

    print(f'✅ {file_type}: {original_size/1024:.1f}KB → {minified_size/1024:.1f}KB '
          f'({savings:.0f}% smaller)')


if __name__ == '__main__':
    print('Minifying files for production...\n')

    # CSS files
    css_files = [
        ('static/css/style.css', 'static/css/style.min.css'),
        ('static/css/admin.css', 'static/css/admin.min.css'),
    ]

    for input_f, output_f in css_files:
        if os.path.exists(input_f):
            minify_file(input_f, output_f, rcssmin.cssmin, 'CSS')

    # JS files
    js_files = [
        ('static/js/main.js',  'static/js/main.min.js'),
        ('static/js/admin.js', 'static/js/admin.min.js'),
    ]

    for input_f, output_f in js_files:
        if os.path.exists(input_f):
            minify_file(input_f, output_f, rjsmin.jsmin, 'JS')

    print('\nDone! Use .min.css and .min.js in production.')
