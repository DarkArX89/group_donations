import csv, os

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from payment.models import Payment, Collect, Reason, User
from group_donations.settings import BASE_DIR


'''
В FILE_DICT указываются названия csv-файлов без расширения и соответствующие
им модели. 
В ID_FIELD_IN_FILE_DIC указываются поля csv-файлов, в которых данные
передаются в виде id для связанных полей (не считая поля с именем id), и
модели, из которых по этим id брать объекты.
В OPTIONAL_FIELDS указываются необязательные для заполнения поля csv-файлов,
и если в таком поле не заадано значение, то перед созданием объекта оно
удаляется.
'''

FILE_DICT = {
    'reasons': Reason,
    'collects': Collect,
    'payments': Payment
}
ID_FIELD_IN_FILE_DICT = {
    'reason': Reason,
    'collect': Collect,
    'author': User,
    'user':User
}
OPTIONAL_FIELDS = ('max_sum',)

class Command(BaseCommand):
    '''Manage command для загрузки данных в БД.'''

    help = 'Import data from CSV to db.sqlite3'

    def handle(self, *args, **options):
        '''
        1. Формируем имя файла для обработки из FILE_DICT.
        2. Проверяем существует ли он и открываем его.
        3. Считываем данные в reader и построчно оборабатываем.
        4. Если в строке есть OPTIONAL_FIELDS - вызываем 
        remove_empty_optional_fields.
        5. Если в строке есть id - вызываем id_to_object.
        6. Создаём объект модели по мтроке.
        '''
        for current_file, model in FILE_DICT.items():
            file_name = ''.join([current_file, '.csv'])
            current_file = os.path.join(BASE_DIR, 'static', 'data', file_name)
            if os.path.isfile(current_file):
                with open(current_file, encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    total = 0
                    for row in reader:
                        row_id = row.get('id')
                        for key in OPTIONAL_FIELDS:    
                            if key in row.keys():
                                self.remove_empty_optional_fields(row, key)
                        for key in row.keys():
                            if key in ID_FIELD_IN_FILE_DICT:
                                self.id_to_object(row, key)
                        try:
                            obj, status = model.objects.get_or_create(**row)
                        except:
                            print(f'Объект файла {current_file} строки '
                                  f'{row_id} не создан из-за ошибки!')
                        if status:
                            total += 1
                print(current_file, ': загружено ', total, ' записей.')
            else:
                print(f'Файл {current_file} не существует! Он пропущен.')
        return 'Импорт успешно завершён!'

    def id_to_object(self, current_row, field_name):
        '''
        По имени поля получает id из строки, по нему находит объект и
        вставляет его обратно в строку вместо значения id.
        '''
        id_value = current_row.get(field_name)
        model = ID_FIELD_IN_FILE_DICT.get(field_name)
        obj = get_object_or_404(model, id=id_value)
        current_row[field_name] = obj

    def remove_empty_optional_fields(self, current_row, field_name):
        '''Удаляет незаполненные необязательные поля из строки.'''
        if current_row.get(field_name) == '':
            del current_row[field_name]