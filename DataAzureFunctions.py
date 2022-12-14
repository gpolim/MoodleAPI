import datetime
import requests
import pandas as pd
import logging
import azure.functions as func
from sqlalchemy import create_engine

url = "MOODLE URL/webservice/rest/server.php"

def _engine_():
    user = ''
    password = ''
    host = ''
    database = ''
    port = ''
    return create_engine(url=f"mssql+pymssql://{user}:{password}@{host}:{port}/{database}")
def get_usuarios():
    params = {
        'wstoken': 'YOUR TOKEN',
        'wsfunction': 'core_user_get_users',
        'criteria[0][key]': 'email',
        'criteria[0][value]':'%',
        'moodlewsrestformat': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()   
    return data
get_usuarios_df = pd.json_normalize(get_usuarios())
get_usuarios_df2 = pd.json_normalize(get_usuarios_df.explode('users').users)
get_usuarios_final = get_usuarios_df2[['id','username','city','country','lang','firstname','lastname','fullname','email','firstaccess','lastaccess'
                        ,'department','suspended']]
get_usuarios_final.to_sql('usuarios_moodle', con=_engine_(), schema='moodle', if_exists='replace', index=False)
def get_categorias():
    params = {
        'wstoken': "YOUR TOKEN",
        'wsfunction': 'core_course_get_categories',
        'moodlewsrestformat': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data
get_categorias_df = pd.json_normalize(get_categorias())
get_categorias_final = get_categorias_df[['id','name','idnumber','description','visible']]
get_categorias_final.to_sql('categorias_moodle', con=_engine_(), schema='moodle', if_exists='replace', index=False)
def get_cursos():
    params = {
    'wstoken': "YOUR TOKEN",
    'wsfunction': 'core_course_get_courses',
    'moodlewsrestformat': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()
    df5 = pd.DataFrame(data)
    df_final = df5[["id", "shortname", "fullname", "format"]]
    df_final.to_sql(con=_engine_(), name='cursos', schema='moodle', if_exists='replace', index=False)
def get_notas(id_curso: int):
    params = {
    'wstoken': "YOUR TOKEN",
    'wsfunction': "gradereport_user_get_grade_items",
    'courseid': f'{id_curso}',
    'moodlewsrestformat': 'json'
    }
    return requests.get(url, params=params).json()
def df_all_notas(lista_cursos: list):
    user_id = []
    course_id = []
    nota = []
    for i, j in lista_cursos:
        notas_curso = get_notas(i)
        for k in notas_curso['usergrades']:
            user_id.append(k['userid'])
            course_id.append(k['courseid'])
            nota.append(k['gradeitems'][j]['graderaw'])
    data = zip(user_id, course_id, nota)
    columns = ('user_id', 'course_id', 'nota')
    df= pd.DataFrame(data=data, columns=columns)
    df["nota"] = df["nota"].apply(lambda x: format(float(x),",.2f"))
    return df
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    _engine_()
    get_usuarios()
    get_cursos()
    get_categorias()
    df_all_notas([(COURSEID,TEST_ID),(COURSEID,TEST_ID)]).to_sql(con=_engine_(), name='notas_usuarios', schema='moodle', if_exists='replace', index=False)
    print("Usuarios Inseridos no Banco de Dados")
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
