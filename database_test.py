from backend.data_manager import DatabaseManager
from backend.data_models import Verb

dm = DatabaseManager()
dm.connect_to_db("New Verb Decksdf")
dm.get_current_db_language()

spanish_tenses_template = {
    'presente_imperfecto': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'preterito_indefinido': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'preterito_imperfecto': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'futuro_imperfecto': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'preterito_perfecto': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'preterito_pluscuamperfecto': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'preterito_anterior': {r'Yo': "sh", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'futuro_perfecto': {r'Yo': "fs", r'El/Ella': "sh", r'Vos': "sh", r'Nosotros(as)': "sh", r'Ustedes': "sh", r'Ellos(as)': "sh"},
    'gerundio': {"gerundio": "ando"},
}

