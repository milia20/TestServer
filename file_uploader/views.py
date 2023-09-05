from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from file_uploader.models import UploadFile, User

from file_uploader.serializers import UploaderSerializer, FileListSerializer, ErrorSerializer

import pandas as pd


class Uploader(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: UploaderSerializer()})
    def post(self, request):
        """Загрузка файла"""
        file = UploadFile.objects.create(owner=self.request.user, file=request.data.get('datafile'))
        return Response(data=UploaderSerializer(file).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={status.HTTP_200_OK: FileListSerializer()})
    def get(self, request):
        """Получение списка всех файлов с информацией об их полях"""
        files = UploadFile.objects.all()
        files_list = []
        for f in files:
            data = pd.read_csv(f.file.path)
            serialized_file = UploaderSerializer(f).data
            serialized_file['fields'] = list(data.columns)
            files_list.append(serialized_file)
        return Response(data=files_list, status=status.HTTP_200_OK)

    # Альтернативный вариант
    # def get(self, request):
    #     files = UploadFile.objects.all()
    #     files_list = []
    #     for f in files:
    #         data = pd.read_csv(f.file.name)
    #         files_list.append({'file': f, 'fields': list(data.columns)})
    #     return Response(data=FileListSerializer(files_list, many=True).data, status=status.HTTP_200_OK)


class Dropper(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(responses={status.HTTP_200_OK: '',
                                    status.HTTP_400_BAD_REQUEST: ErrorSerializer()})
    def get(self, request, *args, **kwargs):
        """Получение информации из файла.
        В URL указывается:
            - filter=Колонка(-и) для фильтрации
            - sort=Колонка(-и), по которым проходит сортировка
            - ascending=Указывается направление сортировки (True/False)
            - json_format=Формат вывода данных из файла"""
        filters = request.query_params.getlist('filter', None)
        sorts = request.query_params.getlist('sort')
        ascends = [False]*len(sorts)
        json_format = request.query_params.get('json_format', None)
        list_ascends = request.query_params.getlist('ascending')
        for i in range(len(list_ascends)) if len(list_ascends) <= len(sorts) else range(len(sorts)):
            if list_ascends[i]!='True' or list_ascends[i]!='False':
                ascends[i] = True
            else:
                ascends[i] = eval(list_ascends[i])
            # try:
            #     ascends[i] = eval(list_ascends[i])
            # except NameError:
            #     ascends[i] = True
        try:
            file = UploadFile.objects.get(file=kwargs['filename'])
            data = pd.read_csv(file.file.path)
            df = data
            if sorts:
                df = df.sort_values(by=sorts, ascending=ascends)
            if filters:
                df = df.filter(items=filters)
            if json_format not in ['split', 'records', 'index', 'columns', 'values', 'table']:
                json_format = 'columns'
            return Response(data=df.to_json(orient=json_format), status=status.HTTP_200_OK)
        except (KeyError, ObjectDoesNotExist) as e:
            return Response(data=ErrorSerializer({'detail': str(e)}).data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={status.HTTP_204_NO_CONTENT: '',
                                    status.HTTP_400_BAD_REQUEST: ErrorSerializer()})
    def delete(self, request, *args, **kwargs):
        """Удаление файла"""
        try:
            file = UploadFile.objects.get(owner=request.user, file=kwargs['filename'])
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist as e:
            return Response(data=ErrorSerializer({'detail': str(e)}).data, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """

    # Отрисовка HTML-шаблона index.html с данными внутри
    return render(
        request,
        'index.html',
        context={},
    )