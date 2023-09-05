from fastapi import FastAPI
import pandas as pd
import ast, datetime

app = FastAPI()

games  = pd.read_csv("./data/csv/games_steam.csv")
reviews =  pd.read_csv("./data/csv/user_review.csv")
items = pd.read_csv("./data/csv/df_items.csv")

@app.get("/")
def init():
    return {"Documentation": "/docs"}


@app.get("/UserData/{User_ID}")
def UserData(User_ID=None):
    # Si a la función no se le pide nada, retorna Nada.
    if User_ID == None: return None

    # Se convierten todos los id de usuarios a formato string para evitar posibles errores o que no se encuentre al usuario
    items['user_id'] = items['user_id'].apply(lambda x: str(x))
    # Se hace la búsqueda en el dataframe de los items.
    items_user = items[items['user_id'] == str(User_ID)]

    # Si la busqueda no obtuvo ningún resultado:
    if items_user.shape[0] == 0:
        # Se declaran las variable que devuelve la función, de la siguiente manera.
        suma_precios = f"No se ha encontrado los items que ha comprado {User_ID}"
        cantItems = "¿?"
    # Si la búsqueda en el dataframe obtuvo al usuario: 
    else:
        # Se obtiene la lista que esta en la columna items.
        list_items = ast.literal_eval(items_user['items'].iloc[0])
        # Se hace la lista que contendrá los ID de los items que habrá que comparar luego con el datafram de juegos.
        list_items_ID = []
        # Se itera dentro de la lista con los item.
        for item in list_items:
            # Se agreaga a la lista vacía los ID de los items.
            list_items_ID.append(item['item_id'])

        # Se crea la lista que contendrá los precios de los items.
        list_prices = []
        # Se itera dentro de la lista con los ID.
        for id in list_items_ID:
            # Se agrega el precio de los items, comparando el ID en el dataframe 'games'.
            list_prices.extend(list(games['price'][games['id'] == float(id)].values))

        # Se itera sobre la lista de precios. Ya que estos precios están en formato texto:
        for n, price in enumerate(list_prices):
            # Intentamos convertirlos a tipo flotante.
            try: list_prices[n] = float(price)
            # Si no se puede, porque el valor es; por ejemplo: "Free to Play", lo convierte a un flotante 0.00
            except ValueError: list_prices[n] = float("0.0")

        # Definimos la variable que retornará la función como la suma de todos
        # los flotantes de dentro de la lista. Solamente con tres decimales.
        suma_precios = round(sum(list_prices),3)

        # Definimos la cantidad de items, como la longitud de la lista que los contiene.
        cantItems = len(list_items)

    # Repetimos el proceso de obtener todos los ID de usuario en formato cadena.
    reviews['user_id'] = reviews['user_id'].apply(lambda x: str(x))
    # Buscamos un ID que sea idéntico en la columna 'user_id' del dataframe "reviews"
    reviews_user = reviews[reviews['user_id'] == str(User_ID)]

    # Si la búsqueda no obtuvo respuestas:
    if reviews_user.shape[0] == 0:
        # Declaramos las funciones que retornará la función para que no haya errores:
        percent = f"No se han encontrado reviews realizadas por el usuario {User_ID}"
        countRecommend = '¿?'
    # Si se obtuvo un resultado en la búsqueda por ID:
    else:
        # Obtenemos la lista del Usuario
        list_reviews = ast.literal_eval(reviews_user['reviews'].iloc[0])
        
        # Definimos los dos contadores:
        countTrue = 0
        countRecommend = 0

        # Iteramos sobre la lista del usuario para obtener las reviews.
        for revw in list_reviews:
            # 
            try:
                # Si la lista no está vacía y contiene al diccionario "revw"
                if revw['item_id'] in list_items_ID:
                    # Solo si el valor de la clave "recommend" es un booleano True
                    if revw['recommend'] is True:
                        # Se agrega uno a ambos contadores.
                        countRecommend += 1
                        countTrue += 1
                    # Sino, solamente se suma al contador de cuantas recomendaciones exiten.
                    else:
                        countRecommend += 1
                
                # Se define la variable que retornará la función como el porcentaje de reviews que recomiendan usar x item.
                percent = round(countRecommend * 100 / len(list_items), 3)
            
            # Si la lista que iteramos está vacía no podrá encontrar un diccionario donde buscar y le decimos que haga lo siguiente:
            except UnboundLocalError:
                # Que agregue uno al contador de items con review.
                countRecommend += 1
                # Define la variable como 
                percent = f"Cantidad de reviews realizadas: {countRecommend}"

    return {
        "Cantidad de dinero gastado por el usuario": suma_precios,
        "Porcentaje de recomendación": percent,
        "Cantidad de items recomendados": countRecommend,
        "Cantidad de items del usuario": cantItems
    }


def changeDatesReviews():
    
    literal_reviews = reviews['reviews'].apply(lambda a: ast.literal_eval(a))

    col_Fechas = [[line['posted'] for line in dict] for dict in literal_reviews]

    fechas = []
    dictionary_months = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
    }

    for lista_de_fechas in col_Fechas:
        lista_iter = []
        for cadena in lista_de_fechas:
            cadena = cadena.replace("Posted ", "")
            cadena = cadena.replace(".","")
            cadena = cadena.replace(",","")
            cadena = cadena.replace(" ", '-')
            for month in dictionary_months:
                cadena = cadena.replace(f"{month}", f"{dictionary_months[f'{month}']}")
            lista_iter.append(cadena)
        fechas.append(lista_iter)

    fechas_2 = []
    for i, lista in enumerate(fechas):
        fechas_dtime = []
        for cadena in lista:
            try:
                date = datetime.datetime.strptime(cadena, '%m-%d-%Y')
            except ValueError:
                cadena = cadena + '-2016'
                date = datetime.datetime.strptime(cadena, '%m-%d-%Y')
            fechas_dtime.append(date)
        fechas_2.append(fechas_dtime)
    return fechas_2


@app.get("/CountReviews/date_i={date_i}&date_f={date_f}")
def CountReviews(date_i, date_f):
    import datetime

    reviews['dates_posted'] = changeDatesReviews()
    
    try:
        init = datetime.datetime.strptime(date_i, "%d-%m-%Y")
        final = datetime.datetime.strptime(date_f, "%d-%m-%Y")
    except ValueError:
        pass

    count_Users = 0
    count_recommend = 0

    dates = [line for line in reviews['dates_posted']]
    literal_reviews = [ast.literal_eval(line) for line in reviews['reviews']]

    countUser = 0
    count_Recommend_Ttal = 0
    count_Recommend_True = 0

    for line in dates:
        for datetime in line:
            entreFechas = init < datetime < final
            if entreFechas is True:
                countUser += 1
                break

    for list_R in literal_reviews:
        for dicc in list_R:
            if dicc['recommend'] is True:
                count_Recommend_Ttal += 1
                count_Recommend_True += 1
            else: count_Recommend_Ttal += 1

    try: percentaje = f"{round(count_Recommend_True * 100 / count_Recommend_Ttal, 3)} %"
    except ZeroDivisionError: percentaje = "No exiten recomendaciones en las reviews."

    return {
        "Cantidad de Usuarios que realizaron reviews": countUser,
        "Porcentaje de usuarios que realizaron una recomendación": percentaje,
        "Cantidad de reviews de items": count_Recommend_Ttal,
        "Cantidad de items recomendados": count_Recommend_True
    }


genres_ranking = pd.read_csv("./data/csv/Genres.csv")

@app.get("/Genre/{genero}")
def Genre(genero: str = None):
    '''
    Los géneros de los que se tiene registro son los siguientes:
        'Indie', 'Simulation', 'Action', 'RPG', 'Adventure',
        'Strategy', 'Free to Play', 'Massively Multiplayer', 'Casual',
        'Racing', 'Early Access', 'Sports', 'Utilities',
        'Design &amp; Illustration', 'Animation &amp; Modeling', 'Video Production',
        'Web Publishing', 'Education', 'Software Training',
        'Audio Production', 'Photo Editing', 'Accounting'
    '''


    df_genre = genres_ranking[genres_ranking['Genero'] == genero]
    if df_genre.shape[0] == 0:
        return {}

    else: 
        df_genre['Ranking'] = df_genre['Ranking'].astype(int)
        df_genre['Cantidad de PlayTime-Forever'] = df_genre['Cantidad de PlayTime-Forever'].astype(int)
        rank, playTime= df_genre['Ranking'].iloc[0] + 1, df_genre['Cantidad de PlayTime-Forever'].iloc[0]
        return {
            "Género": genero,
            "Puesto en el ranking": f"{rank}",
            "Cantidad de veces jugado": f"{playTime}"
        }