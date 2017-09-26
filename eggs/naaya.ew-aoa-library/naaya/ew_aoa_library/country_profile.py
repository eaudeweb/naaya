# coding=utf-8
from zope.publisher.browser import BrowserPage
#from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from jsmap import (country_code, region_code, region_name, region_countries,
                   country_name)


country_contributors = {
    "Albania": ["Etleva Canaj", "Auron Meneri", "Luan Ahmetaj", "Erinda Misho"],
    "Armenia": ["Julieta Ghlichyan"],
    "Austria": ["Johannes Mayer", "Elisabeth Freytag", "Florian Wolf-Ott", "Hubert Reisinger", "Sabine Kranzl"],
    "Azerbaijan": ["Rashad Allahverdiyev"],
    "Belarus": ["Svetlana Utochkina", "Saveliy Kuzmin", "Alexander Stankevich"],
    "Belgium": ["Jan Voet", "Line Vancraeynest", "Veronique Verbeke", "Hugo Van Hooste", "Nathalie Dewolf", "Vincent Brahy", "Maene Soetkin", "Caroline De Geest", "Stijn Overloop", "Myriam Bossuyt", "Bob Peeters", "Saskia Opdebeeck", "Erika Van Der Putten", "Johan Brouwers"],
    "Bosnia and Herzegovina": ["Mehmed Cero", "Goran Krstovic"],
    "Bulgaria": ["Camelia Dikova", "Krasimira Avramova", "Detelina Peicheva"],
    "Croatia": ["Jasna Butuči", "Rene Vukelić"],
    "Cyprus": ["Christina Pantazi"],
    "Czech Republic": ["Jirí Hradec", "Premysl Stepanek", "Lukas Pokorny", "Simona Losmanova"],
    "Denmark": ["Esben Tind"],
    "Estonia": ["Leo Saare", "Marion Leppik"],
    "Finland": ["Tapani Säynätkari"],
    "Former Yugoslav Republic of Macedonia": ["Svetlana Gjorgjeva"],
    "France": ["Jacques Thorette"],
    "Georgia": ["Mikheil Tushishvili", "Nino Sharashidze"],
    "Germany": ["Christina Pykonen", "Heide Jekel"],
    "Greece": ["Dimitris Meimaris"],
    "Hungary": ["Gabriella Pajna"],
    "Iceland": ["Gunnar Jónsson"],
    "Ireland": ["Micheal Lehane"],
    "Italy": ["Claudio Maricchiolo", "Maria Concetta Giunta", "Rita Calicchia", "Anna Luise"],
    "Kazakhstan": ["Olga Suvorova"],
    "Kyrgyzstan": ["Baglan Salikmambetova"],
    "Kosovo under UN Security Council Resolution 1244": ["Rizah Hajdari", "Afrim Berisha"],
    "Latvia": ["Vita Slanke"],
    "Liechtenstein": ["Roland Jehle"],
    "Lithuania": ["Liutauras Stoškus"],
    "Luxembourg": ["Eric De Brabanter"],
    "Malta": ["Saviour Formosa", "Antoine Zahra", "Priscilla Scerri"],
    "Montenegro": ["Dragan Asanović", "Milena Bataković"],
    "Republic of Moldova": ["Maria Nagornii", "Tamara Guvir", "Valentina Tapis", "Tatiana Plesco", "Vasile Scorpan"],
    "the Netherlands": ["Kees Schotten", "Hiddo Huitzing"],
    "Norway": ["Rebekka Borsch", "Kari Holden"],
    "Poland": ["Lucyna Dygas-Ciołkowska", "Barbara Albiniak", "Ewa Palma", "Lukasz Tomaszewski"],
    "Portugal": ["Regina Vilao", "Diana Carlos", "Sónia Costa", "João Varela", "Carlos Carvalho", "Susana Alvarez", "Cláudia Pina", "Francisco Vala", "Teresa Larsson", "David Alves", "Filomena Lobo", "Maria de Fátima Espírito Santo Coelho", "Eduardo Santos", "António Leitão", "Ana Marçal", "Ana Teixeira", "Luísa Silvério", "Ana Sofia Vaz", "Isabel Tomé de Andrade", "Maria Ângela Pais da Graça Lobo", "Maria InêsTrigo", "Maria João Cabral", "Luísa Rodrigues", "Marina Sequeira", "João Loureiro", "Pedro Ivo Arriegas"],
    "Romania": ["Gabriela Vasiliu-Isac", "Camelia Vasile", "Dorina Mocanu"],
    "Russian Federation": ["Alexander Shekhovtsov", "George A. Fomenko", "Yuliy Kunin"],
    "Serbia": ["Dejan Lekić", "Danijela Stamenković", "Dijana Čvoro"],
    "Slovakia": ["Katarìna Kosková", "Peter Kapusta"],
    "Slovenia": ["Jelko Urbančič"],
    "Spain": ["Marta Muñoz Cuesta", "Javier Cachón de Mesa"],
    "Sweden": ["Ninni Borén"],
    "Switzerland": ["Nicolas Perritaz", "Celine Girard"],
    "Tajikistan": ["Khursheda Musavirova"],
    "Turkey": ["A. Çagatay Dikmen", "Şule Ataman"],
    "Turkmenistan": ["Bekmyrat Eyeberdijev"],
    "Ukraine": ["Valentyna Vasylenko", "Liliia Kozak", "Georgiy Veremiychyk", "Larisa Yurchak", "Tatiana Gerasymenko", "Alexander Vasenko"],
    "the United Kingdom": ["James Tucker"],
    "Uzbekistan": ["Lyudmila Aksyonova", "Majid Khodjaev", "Mukhammadi Mamanazarov", "Artur Mustafin", "Kamaliddin Sadikov"],
}



country_profile_zpt = NaayaPageTemplateFile('zpt/country_profile.zpt', globals(), 'aoa_country_profile')

class CountryProfileView(BrowserPage):

    def __call__(self):
        ctx = self.aq_parent
        options = {
            'country_names': sorted(country_code,
                                    key=lambda x: x.lstrip('the ')),
            'country_contributors': country_contributors,
        }
        return country_profile_zpt.__of__(ctx)(**options)



region_info_zpt = NaayaPageTemplateFile('zpt/region_info.zpt', globals(), 'aoa_region_info')

class RegionInfoView(BrowserPage):

    def __call__(self):
        ctx = self.aq_parent
        options = {
            'region_names': sorted(region_code),
            'region_countries': region_countries,
            'region_code': region_code,
            'country_name': country_name,
        }
        return region_info_zpt.__of__(ctx)(**options)
