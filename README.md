# Practica 1: Web Scraping

## Descripción

Esta práctica se ha realizado bajo el contexto de la asignatura Tipología y ciclo de vida de los datos, perteneciente al Máster en Ciencia de Datos de la Universitat Oberta de Catalunya. En ella, se aplican técnicas de web scraping mediante el lenguaje de programación Python para extraer así datos de la web Muebles LUFE y generar un dataset.

## Miembros del equipo

La actividad ha sido realizada de manera individual por **Pablo A. Delgado**.

## Ficheros del código fuente

- **src/main.py**: punto de entrada al programa. Inicia el proceso de scraping.
- **src/scraper.py**: contiene la implementación de la clase CompetitorScraper cuyos métodos generan el dataset en formato csv a partir de los datos extraidos de las publicaciones de productos en el sitio web de Muebles LUFE.

## Ejecucion del scraper

Para ejecutar el script es necesario tener instalados los siguientes modulos adicionales en python:

    pandas
    beautifulsoup4
    requests
    json
    
y para ejecutar el scraper propiamente dicho simplemente realizar esto desde la consola:

    python main.py
    
O si se desea ejecutar el scraper desde por ej jupyter notebook, se puede ejecutar los siguientes comandos:

    from scrapers import CompetitorScraper
    
    scraper = CompetitorScraper()   # creamos una instancia del scraper
    scraper.scrape()                # ejecutamos el metodo que inicia el proceso de scraping. 
    
El tiempo promedio que le toma al scraper recuperar toda la data del sitio es de aproximadamente 40 minutos. Terminado ese tiempo, se puede consultar el resultado del scraping
desde el panda dataframe resultante, ejecutando por ejemplo:

    scraper.df_data.head()
    
Mientras que si desea guardar el dataframe en un fichero csv podemos ejecutar:

    filename = '~/dataset_resultante.csv'
    scraper.data2csv(filename)
    
El fichero resultante contendra esta informacion:

* _**Title**_: Nombre del producto.
* _**Price**_: Precio del producto.
* _**Category_path**_: categoría a la cual pertenece el producto.
* _**Rating**_: el rating es el promedio de las calificaciones recibidas por parte de los compradores del producto.
* _**Qty_califications**_: cantidad de calificaciones recibidas.
* _**Features_JSON_format**_: se guarda en un solo campo y en formato JSON las medidas y/o características del producto. 
* _**Image_Url**_: url de la primera imagen del producto en la publicación.
* _**Item_Url**_: url del producto dentro del sitio web.

## Recursos

- Subirats, L., Calvo, M. (2019). Web Scraping. Editorial UOC.
- Masip, D. (2010). El lenguaje Python. Editorial UOC.
- Tutorial de Github https://guides.github.com/activities/hello-world.
- Lawson, R. (2015). Web Scraping with Python. Packt Publishing Ltd. Chapter 2. Scraping the Data.
- Get DOI for a github repo: https://guides.github.com/activities/citable-code/
