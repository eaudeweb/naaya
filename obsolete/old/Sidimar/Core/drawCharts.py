
#Python imports
import matplotlib
matplotlib.use('Agg')
from pylab import *
#from os import *
from StringIO import StringIO
from PIL import Image as PILImage
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import FormatStrFormatter

colors_codes = {
    #Sedimenti
    'SAL2': '#669acc',  #Alluminio
    'DAS2': '#ff8844',  #Arsenico
    'DCD2': '#0aaaa2',  #Cadmio
    'DCR2': '#b76bb6',  #Cromo
    'SFE2': '#995466',  #Ferro
    'DCU2': '#67bb89',  #Rame
    'DHG2': '#859ba8',  #Mercurio
    'DNI2': '#fe322b',  #Nichel
    'DPB2': '#757a98',  #Piombo
    'DVV2': '#327854',  #Vanadio
    'DZN2': '#ff6766',  #Zinco
    'S04T': '#0000ff',  #Tributilstagno
    'S100': '#0000ff',  #Spore clostridi solfitoriduttori
    'DC02': '#00ff00', #Carbonio organico
    #Molluschi
    'DAL1': '#669acc',  #Alluminio
    'DAS1': '#ff8844',  #Arsenico
    'DCD1': '#0aaaa2',  #Cadmio
    'DCR1': '#b76bb6',  #Cromo
    'DFE1': '#995466',  #Ferro
    'DCU1': '#67bb89',  #Rame
    'DHG1': '#859ba8',  #Mercurio
    'DNI1': '#fe322b',  #Nichel
    'DPB1': '#757a98',  #Piombo
    'DVV1': '#327854',  #Vanadio
    'DZN1': '#ff6766',  #Zinco
    'I04T': '#0000ff',  #Tributilstagno
}

more_colors = [
    '#35648C', '#E0C6AF', '#A9A640', '#CAB8CB', '#A96040',
    '#CBD8D8', '#596790', '#D6D6C3', '#C8906F', '#DDD6DD',
    '#6F6D2A', '#EAE3C9', '#75538A', '#BFCCCB', '#A36E6E',
    '#C6D6DD', '#536E53', '#EED3D3', '#918F58', '#BFC6CC',
    '#BE5353'
]

pie_colors = ['#BDCAD7', '#999900', '#FFCCCC', '#046209', '#C0DEED', 
    '#993333', '#BDD7D7', '#CC3366', '#FFCC99', '#003366', '#FFF2BD', 
    '#333300', '#E5D7E5', '#FF6600', '#E5E5BD', '#990099', '#C9E4E4', 
    '#993300', '#CC99CC', '#FFBB39', '#F5B6AE', '#CC0000', '#E2DBE6', 
    '#FE5513', '#CCD0DF', '#AAEA00', '#FEE0D5', '#07BA3E', '#CDDCF0', 
    '#C36F4E', '#CCDBDF', '#D7606B', '#FFEBAF', '#002DC2', '#FBFECB', 
    '#709A00', '#EADFE7', '#FFBB39', '#E2EACB', '#EA00AA', '#6A8DCB', 
    '#EA8900', '#D6AFCC', '#AAEA00', '#FE1313', '#CCD6DF', '#EAE100', 
    '#FED5D5', '#07BA0B', '#CDE6F0', '#C34E4E', '#CCDFDF', '#D7608D', 
    '#FFD4AF', '#0068C2', '#FEF3CB', '#9A9400', '#EADFEA', '#FF8339', 
    '#EAE9CB', '#E100EA', '#D4E9E8', '#EA4700', '#D5AFD6', '#EAE100']

class drawCharts:
    """
    Layer over matplotlib library for generating charts.
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def save_to_string(self, imgsize, imgbuf):
        """
        Given a string that represents an image, create an Image object
        in temp_folder object.
        """
        imgobject = PILImage.fromstring('RGB', imgsize, imgbuf, 'raw', 'RGB', 0, 1)
        imgdata = StringIO()
        imgobject.save(imgdata, 'PNG')
        return imgdata.getvalue()

    def create_figure(self, fdpi, fwidth, fheight, fcolor, fgrid=1, gcolor='#acacac'):
        """
        Create a new figure object
        """
        clf()
        fobject = figure(fdpi, figsize=(fwidth/fdpi, fheight/fdpi), facecolor=fcolor, edgecolor=fcolor)
        #set frame
        setp(gca().get_frame(), edgecolor=fcolor)
        #activate and set grid
        if fgrid:
            grid(True)
            setp(gca().get_xgridlines(), linestyle='None')
            setp(gca().get_ygridlines(), color=gcolor)
        #set X axe labels
        setp(gca().get_xticklabels(), rotation=10, size=7)
        #set and format Y axe
        majorFormatter = FormatStrFormatter('%s')
        gca().yaxis.set_major_formatter(majorFormatter)
        return fobject

    def export_close_figure(self, fobject):
        """
        Export as a string and close the figure.
        """
        canvas = FigureCanvasAgg(fobject)
        canvas.draw()
        size, buf = canvas.get_width_height(), canvas.tostring_rgb()
        #close and return data
        close()
        return size, buf

    def geg(self, gtitle='', gsize='small'):
        """
        Generate an empty image.
        """
        if gsize == 'big':
            fdpi, fwidth, fheight, fcolor = 72, 640, 350, '#abcdf0'
        else:
            fdpi, fwidth, fheight, fcolor = 72, 400, 300, '#abcdf0'
        #create a new figure
        fobject = self.create_figure(fdpi, fwidth, fheight, fcolor)
        #set graph title
        title(gtitle, {'fontsize': 18})
        #export and close the figure
        return self.export_close_figure(fobject)

    def gsvbg(self, gkey='', gtitle='', gvalues=[], glabels=[]):
        """
        Generate a simple vertical bar graph.
        """
        gcolor, glen = colors_codes[gkey], len(gvalues)
        fdpi, fwidth, fheight, fcolor, gwidth = 72, 400, 300, '#abcdf0', 0.7
        #create a new figure
        fobject = self.create_figure(fdpi, fwidth, fheight, fcolor, gcolor=gcolor)
        #set graph title
        title(gtitle, {'fontsize': 18})
        #draw graph
        ind = arange(glen)
        for x in bar(ind, gvalues, gwidth, color=gcolor):
            setp(x, edgecolor=gcolor)
        xticks(ind+gwidth/2, glabels)
        xlim(-gwidth/2, glen)
        setp(gca().get_yticklabels(), size=6)
        #export and close the figure
        return self.export_close_figure(fobject)

    def gmvbg(self, gtitle='', gvalues=[], glabels=[], glegend=[]):
        """
        Generate a multiple vertical bar graph.
        """
        glen = len(gvalues)
        fdpi, fwidth, fheight, fcolor, gwidth = 72, 640, 350, '#abcdf0', 0.7/float(glen)
        #create a new figure
        fobject = self.create_figure(fdpi, fwidth, fheight, fcolor, fgrid=1)
        #set graph title
        title(gtitle, {'fontsize': 18})
        #draw graph
        ind = arange(len(gvalues[0]))
        buf = 0
        leg = []
        for i in range(0, glen):
            gcolor = more_colors[i]
            p = bar(ind+buf, gvalues[i], gwidth, color=gcolor)
            leg.append(p[0])
            for x in p:
                setp(x, edgecolor=gcolor)
            buf = buf + gwidth
        xticks(ind+gwidth*glen/2, glabels)
        xlim(-gwidth*glen/2, len(ind))
        setp(gca().get_yticklabels(), size=6)
        #figlegend(leg, glegend, loc='upper right')
        #export and close the figure
        return self.export_close_figure(fobject)

    def gclegend(self, glegend=[], loc='center left', gcolors=more_colors):
        """
        Generate a legend for a multiple vertical bar graph.
        """
        glen = len(glegend)
        gwidth, gheight, gstep = 0.25, 0.1, 0.1
        fdpi, fwidth, fheight, fcolor = 72, 300, glen*(gheight+gstep), '#abcdf0'
        #create a new figure
        clf()
        fobject = figure(fdpi, figsize=(fwidth/fdpi, fheight), facecolor=fcolor, edgecolor=fcolor)
        #draw legend
        ax = gca()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
        leg = []
        for i in range(0, glen):
            gcolor = gcolors[i]
            leg.append(Rectangle((0, 0), gwidth, gheight, fill=True, facecolor=gcolor, edgecolor=gcolor)
            )
        figlegend(leg, glegend, loc=loc)
        #export and close the figure
        return self.export_close_figure(fobject)

    def gpg(self, gtitle='', gvalues=[], glabels=[], showlabels=0):
        """
        Generate a pie chart.
        """
        fdpi, fwidth, fheight, fcolor, ecolor = 72, 4, 4, '#ffffff', '#abcdf0'
        #create a new figure
        fobject = figure(fdpi, figsize=(4, 4), facecolor=fcolor, edgecolor=ecolor)
        ax = axes([0.1, 0.1, 0.8, 0.8])
        #set graph title
        title(gtitle, {'fontsize': 18})
        #draw graph
        if showlabels:
            p = pie(gvalues, labels=glabels, colors=pie_colors, shadow=False)
        else:
            p = pie(gvalues, colors=pie_colors, shadow=False)
        #export and close the figure
        return self.export_close_figure(fobject)
