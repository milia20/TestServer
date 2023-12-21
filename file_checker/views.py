from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from sys import exc_info
from .models import Task, UploadedFile
from .forms import TaskForm
from .serializers import FileUploadSerializer, FileListSerializer, ErrorSerializer

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

import pandas as pd


def index(request):
    tasks = Task.objects.order_by('-id')
    return render(request, "file_checker/index.html",
                  {'title': 'Main Page', 'tasks': tasks})


def upload(request):
    error = ''
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('file_checker:main')
        else:
            error = 'Форма не верна'

    form = TaskForm()
    context = {
        'form': form,
        'error': error
    }
    return render(request, "file_checker/upload.html",
                  context)


class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # you can access the file like this from serializer
            # uploaded_file = serializer.validated_data["file"]
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class Uploader(APIView):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: FileUploadSerializer()})
    def post(self, request):
        """Загрузка файла"""
        mes = {'owner': request.user,
               'data': request.data}
        # serializer = self.serializer_class(owner=self.request.user, data=request.data)
        serializer = FileUploadSerializer(data=mes)
        if serializer.is_valid():
            # file = UploadedFile.objects.create(title=request.FILES['filename'].name,
            #                                                 file=request.data.get('datafile'))
            serializer.save()
            # return Response(data=FileUploadSerializer(file).data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(responses={status.HTTP_200_OK: FileListSerializer()})
    def get(self, request):
        """Получение списка всех файлов с информацией об их полях"""
        files = UploadedFile.objects.all()
        files_list = []
        for f in files:
            data = pd.read_csv(f.file.path)
            serialized_file = FileUploadSerializer(f).data
            serialized_file['fields'] = list(data.columns)
            files_list.append(serialized_file)
        return Response(data=files_list, status=status.HTTP_200_OK)


class Dropper(APIView):
    # permission_classes = [IsAuthenticatedOrReadOnly]

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
            if list_ascends[i] != 'True' or list_ascends[i] != 'False':
                ascends[i] = True
            else:
                ascends[i] = eval(list_ascends[i])
            # try:
            #     ascends[i] = eval(list_ascends[i])
            # except NameError:
            #     ascends[i] = True
        try:
            file = UploadedFile.objects.get(file=kwargs['filename'])
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
                                    status.HTTP_400_BAD_REQUEST: ErrorSerializer(),
                                    status.HTTP_401_UNAUTHORIZED: PermissionDenied(),
                                    status.HTTP_401_UNAUTHORIZED: 'TypeError'})
    def delete(self, request, *args, **kwargs):
        """Удаление файла"""
        try:
            file = UploadedFile.objects.get(owner=request.user, file=kwargs['filename'])
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist as e:
            return Response(data=ErrorSerializer({'detail': str(e)}).data,
                            status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response(data=ErrorSerializer({'detail': str(e)}).data,
                            status=status.HTTP_401_UNAUTHORIZED)
        except TypeError:
            return Response(data=ErrorSerializer({'detail': exc_info()}).data,
                            status=status.HTTP_401_UNAUTHORIZED)
