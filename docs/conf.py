import alabaster
import vetoes

project = 'vetoes'
copyright = 'AWeber Communications, Inc.'
version = vetoes.version
release = '.'.join(str(v) for v in vetoes.version_info[:2])

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
master_doc = 'index'
source_suffix = '.rst'

pygments_style = 'sphinx'
html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
html_sidebars = {'**': ['about.html', 'navigation.html']}
intersphinx_mapping = {
    'python': ('http://docs.python.org/3/', None),
    'rejected': ('http://rejected.readthedocs.io/en/latest/', None),
}
