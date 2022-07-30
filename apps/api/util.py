from datetime import datetime


def time_8601(time=datetime.now()) -> str:
    return time.astimezone().isoformat()

def get_class_object(class_path:str):
    from importlib import import_module

    module_path, class_name = class_path.rsplit('.', 1)
    module = import_module(module_path)

    return getattr(module, class_name)

def get_data(algo_id:str, user_idS:str=None):
    '''
    Get data from data table, created pandas DF (parse all the dict and convert them into columns)
    :param algo_id:
    :param user_id:
    :return: pandas DF
    '''

    pass

# obj = get_class_object("apps.learning_models.RandomSampling.RandomSampling")
# result = obj().run()