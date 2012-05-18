#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from scrapy.contrib.loader import XPathItemLoader
from scrapy.item import Item, Field
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

import MySQLdb
from gi.repository import Gtk, GdkPixbuf, Gdk
import sys

class Search:
    busqueda = None
    def getbusqueda(self):
        return self.busqueda
    def setbusqueda(self,value):
        self.busqueda = value

search = Search()

def decodifica(value):
    if value == None:
        encoding = ''
    else:
        encoding = value
        if not isinstance(encoding, unicode):
          encoding = unicode(encoding, 'utf-8')

        encoding = encoding.encode('utf-8')
        encoding = '"' + str(encoding).replace('\'','').replace('"','') + '"'
    
    return encoding

class DB:
    conexion = None
    micursor = None

    def __init__(self):
        """Crea la base de datos""" 
        self.conexion = MySQLdb.connect('localhost','conan','crom','DBdeConan')
        self.micursor = self.conexion.cursor(MySQLdb.cursors.DictCursor)
        query = "CREATE TABLE book (id INT NOT NULL AUTO_INCREMENT, Nombre VARCHAR(100), Autor VARCHAR(100), Editorial VARCHAR(100), Fecha INT(4),Precio VARCHAR(5),Link VARCHAR(255),PRIMARY KEY (id) );"
        self.micursor.execute(query)
        self.conexion.commit()


    def destroy(self):
        """Destruye la base de datos"""
        self.conexion.commit()
        query = "DROP TABLE book;"
        self.micursor.execute(query)
        self.micursor.close()
        self.conexion.close()

class BookItem(Item):
    Nombre = Field()
    Autor = Field()
    Editorial = Field()
    Fecha = Field()
    Link = Field()
    Precio = Field()
    Imagen = Field()



db = DB()

class GUI:
    print "CARGADA"
    builder = ''
    db = db

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("interfaz.glade")

        self.handlers = {
                        "onDeleteWindow": self.destroy,
                        "onSearchMenu": self.menuSearch,
                        "consultaEvent": self.menuOpcionesConsultar,
                        "eliminaEvent": self.menuOpcionesEliminar,
                        "modificaEvent": self.menuOpcionesModificar,
                        "onAboutMenu": self.menuAbout,
                        "gtk_main_quit": self.confirmarSalida,
                        "onButtonClick": self.onButtonClick,
                        "onSelectID":self.onSelectID,
                        "onSelectName":self.onSelectName,
                        "onAboutClose":self.onAboutClose,

                        }
        
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("window1")
        self.window.show_all()
    
    def destroy(self,window):
        if self.db:
            self.db.destroy()
        window = self.builder.get_object("dialog1")
        window.show_all()

    def confirmarSalida(self,window):
        print "Hasta pronto!!"
        Gtk.main_quit()

    def menuSearch(self,entry):
        print "Has pulsado menu buscar"

    def onButtonClick(self,button):
        if (button.get_label() == "Buscar"):
            entradaBuscar = self.builder.get_object("entry1")
            search.setbusqueda(decodifica(entradaBuscar.get_text()))
            entradaBuscar.set_sensitive(False)
            
            botonBuscar = self.builder.get_object("button1")
            botonBuscar.set_sensitive(False)
            scrapeando()
            self.menuOpcionesConsultar(self)

        if (button.get_label() == "Volver"):
            print "Destroy la BD"
            windows = self.builder.get_object("window1")
            windows.show_all()
            parent = self.builder.get_object("window2")
            parent.hide()
            if self.db:
                self.db.destroy()
                self.db.__init__()
            entradaBuscar = self.builder.get_object("entry1")
            entradaBuscar.set_sensitive(True)

            botonBuscar = self.builder.get_object("button1")
            botonBuscar.set_sensitive(True)

    def menuOpcionesConsultar(self,entry):
        windows = self.builder.get_object("window2")
        windows.show_all()
        parent = self.builder.get_object("window1")
        parent.hide()
        print "Has pulsado menuOpcionesConsultar"
 
        #id = self.builder.get_object("label2")
        #id.set_sensitive(True)
        idText = self.builder.get_object("comboboxtext1")
        idText.set_sensitive(True)

        nombre = self.builder.get_object("comboboxtext2")
        nombre.set_sensitive(True)

        #boton = self.builder.get_object("button3")
        #boton.set_label("Obtener")

        query = "SELECT id FROM book WHERE 1;"

        self.db.micursor.execute(query)
        id = self.db.micursor.fetchall()
        idText.remove_all()
        for i in id:
            idText.insert(-1,None,str(i['id']))

        query = "SELECT Nombre FROM book;"

        self.db.micursor.execute(query)
        id = self.db.micursor.fetchall()
        nombre.remove_all()
        for i in id:
            nombre.insert(-1,None,str(i['Nombre']))

    def onSelectName(self,entry):
        nombreEntrada = self.builder.get_object("comboboxtext2")
        nombre = nombreEntrada.get_active_text()

        query = "SELECT * FROM book WHERE Nombre="+ str(nombre) +";"
        self.db.micursor.execute(query)

        registros = self.db.micursor.fetchone()
        print registros


        idEntrada = self.builder.get_object("comboboxtext1")
        id = idEntrada.set_active(int(registros['id']))

        autorEntrada = self.builder.get_object("entry2")
        autor = autorEntrada.set_text(str(registros['Autor']))

        editorialEntrada = self.builder.get_object("entry3")
        editorial = editorialEntrada.set_text(str(registros['Editorial']))

        editorialEntrada = self.builder.get_object("entry4")
        editorial = editorialEntrada.set_text(str(registros['Fecha']))

        precioEntrada = self.builder.get_object("entry5")
        precio = precioEntrada.set_text(str(registros['Precio']))

        precioEntrada = self.builder.get_object("linkbutton1")
        precioEntrada.set_uri(str(registros['Link']))    

        precio = precioEntrada.set_label(str(registros['Link']))

    def onSelectID(self,entry):
        idEntrada = self.builder.get_object("comboboxtext1")
        id = idEntrada.get_active_text()

        query = "SELECT * FROM book WHERE id="+ str(id) +";"
        self.db.micursor.execute(query)

        registros = self.db.micursor.fetchone()
        print registros

        nombreEntrada = self.builder.get_object("comboboxtext2")
        nombre = nombreEntrada.set_active(int(registros['id']))

        autorEntrada = self.builder.get_object("entry2")
        autor = autorEntrada.set_text(str(registros['Autor']))

        editorialEntrada = self.builder.get_object("entry3")
        editorial = editorialEntrada.set_text(str(registros['Editorial']))

        editorialEntrada = self.builder.get_object("entry4")
        editorial = editorialEntrada.set_text(str(registros['Fecha']))

        precioEntrada = self.builder.get_object("entry5")
        precio = precioEntrada.set_text(str(registros['Precio']))

        precioEntrada = self.builder.get_object("linkbutton1")
        precioEntrada.set_uri(str(registros['Link']))    

        precio = precioEntrada.set_label(str(registros['Link']))    



    def menuOpcionesEliminar(self,entry):
        print "Has pulsado menuOpcionesEliminar"
 
    def menuOpcionesModificar(self,entry):
        print "Has pulsado menuOpcionesModificar"

    def menuAbout(self,entry):
        windows = self.builder.get_object("aboutdialog1")     
        windows.show_all()

    def onAboutClose(self, *args):
        self.about = self.builder.get_object("aboutdialog1")
        self.about.hide()

class BookSpider(BaseSpider):
    name = "bookspider"
    #start_urls = ['http://www.casadellibro.com/busqueda-libros?busqueda='+str(busqueda)]
    #print start_urls
    busqueda = None

    def __init__(self):
        url = 'http://www.casadellibro.com/busqueda-libros?busqueda='+decodifica(self.busqueda)
        print url   

    def start_requests(self):
        url = 'http://www.casadellibro.com/busqueda-libros?busqueda='+decodifica(self.busqueda).replace('\"','')
        print url
        yield self.make_requests_from_url(url)

    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        libro = BookItem()

        book_list = hxs.select('//div[@class="mod-list-bigpic mod-libros-formato01 style01"]')

        for xs in book_list:
            libro['Nombre'] = xs.select('.//div[@class="txt"]/a[@class="title-link"]/text()').extract()
            libro['Autor'] = xs.select('.//a[@class="author-link"]/text()').extract()
            libro['Editorial'] = xs.select('.//div[@class="mod-libros-editorial"]/text()').re(r"\w+[( -_){1}\w+]+|[\w']+")
            libro['Fecha'] = xs.select('.//div[@class="mod-libros-editorial"]/span/text()').extract()
            libro['Precio'] = xs.select('//p[@class="price"]/text()').extract()
            libro['Link'] = xs.select('.//div[@class="txt"]/a[@class="title-link"]/@href').extract()


        return libro

def scrapeando():
    from scrapy import signals
    from scrapy.xlib.pydispatch import dispatcher

    def catch_item(sender, item, **kwargs):
        """Rellenamos la BD"""
        for i in enumerate(item.items()):
            x = i[0]
            query = "INSERT INTO book (Nombre ,Autor, Editorial ,Fecha, Precio, Link) VALUES ("+decodifica(item['Nombre'][x])+","+decodifica(item['Autor'][x])+","+decodifica(item['Editorial'][x])+","+decodifica(item['Fecha'][x])+","+decodifica(item['Precio'][x])+","+decodifica("http://www.casadellibro.com"+item['Link'][x])+");"
            db.micursor.execute(query)
            db.conexion.commit()
        print item

    dispatcher.connect(catch_item, signal=signals.item_passed)

    from scrapy.conf import settings
    settings.overrides['LOG_ENABLED'] = False

    from scrapy.crawler import CrawlerProcess

    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    book = BookSpider()
    book.busqueda=unicode(search.getbusqueda())
    crawler.crawl(book)
    print "Start scraping to la Casa del Libro"
    crawler.start()
    print "End scraping to la Casa del Libro"
    crawler.stop()

def main():

    app = GUI()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
