from StringIO import StringIO
from path import path
import requests
import PIL.Image


theme_names = [
    'coast_sea', 'regions', 'urban', 'air', 'biodiversity', 'chemicals',
    'climate', 'human', 'landuse', 'natural', 'noise', 'soil', 'waste',
    'water', 'other_issues', 'agriculture', 'energy', 'fishery',
    'households', 'industry', 'economy', 'tourism', 'transport',
    'technology', 'policy', 'scenarios',
]

themes_path = path(__file__).parent.parent/'static'/'themes'


def get_and_resize(name, target_size):
    url = 'http://www.eea.europa.eu/themes/%s/theme_image/image_large' % name
    data = requests.get(url).content
    image = PIL.Image.open(StringIO(data))
    image.thumbnail(target_size)
    out_path = themes_path/'%s-40.png' % name
    image.save(out_path)
    print out_path


def main():
    for name in theme_names:
        get_and_resize(name, (40, 30))

if __name__ == '__main__':
    main()
