from .crud_common import App as BaseApp
from morpfw.crud.model import Collection, Model
from morpfw.crud.schema import Schema
from morpfw.crud.storage.elasticsearchstorage import ElasticSearchStorage
from .crud_common import get_client, run_jslcrud_test, PageCollection, PageModel
from .crud_common import NamedObjectCollection, NamedObjectModel
import pprint
from more.transaction import TransactionApp
from morepath.reify import reify
from morepath.request import Request
from more.basicauth import BasicAuthIdentityPolicy
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register as register_session
import morpfw.crud.signals as signals
from elasticsearch import Elasticsearch
import jsonobject

Session = sessionmaker()
register_session(Session)


class ESClientRequest(Request):

    @reify
    def es_client(self):
        return Elasticsearch(hosts='127.0.0.1:9085')


class App(BaseApp, TransactionApp):

    request_class = ESClientRequest


class PageStorage(ElasticSearchStorage):
    index_name = 'test-index'
    doc_type = 'page'
    refresh = 'wait_for'
    model = PageModel


@App.path(model=PageCollection, path='pages')
def collection_factory(request):
    storage = PageStorage(request)
    return PageCollection(request, storage)


@App.path(model=PageModel, path='pages/{identifier}')
def model_factory(request, identifier):
    storage = PageStorage(request)
    return storage.get(identifier)


class ObjectSchema(Schema):

    id = jsonobject.StringProperty(required=False)
    uuid = jsonobject.StringProperty(required=False)
    body = jsonobject.StringProperty(required=True, default='')
    created_flag = jsonobject.BooleanProperty(required=False, default=False)
    updated_flag = jsonobject.BooleanProperty(required=False, default=False)


@App.identifierfields(schema=ObjectSchema)
def object_identifierfields(schema):
    return ['id']


@App.default_identifier(schema=ObjectSchema)
def object_default_identifier(schema, obj, request):
    return None


class ObjectModel(Model):
    schema = ObjectSchema


class ObjectCollection(Collection):
    schema = ObjectSchema


@App.subscribe(signal=signals.OBJECT_CREATED, model=ObjectModel)
def object_created(app, request, obj, signal):
    obj.data['created_flag'] = True


@App.subscribe(signal=signals.OBJECT_UPDATED, model=ObjectModel)
def object_updated(app, request, obj, signal):
    obj.data['updated_flag'] = True


class ObjectStorage(ElasticSearchStorage):
    index_name = 'test-index'
    doc_type = 'object'
    refresh = 'wait_for'
    auto_id = True
    model = ObjectModel


@App.json(model=ObjectCollection, name='get_uuid')
def get_object_by_uuid(context, request):
    uuid = request.GET.get('uuid')
    return context.get_by_uuid(uuid).json()


@App.path(model=ObjectCollection, path='objects')
def object_collection_factory(request):
    storage = ObjectStorage(request)
    return ObjectCollection(request, storage)


@App.path(model=ObjectModel, path='objects/{identifier}')
def object_model_factory(request, identifier):
    storage = ObjectStorage(request)
    return storage.get(identifier)


class NamedObjectStorage(ElasticSearchStorage):
    index_name = 'test-index'
    doc_type = 'namedobject'
    refresh = 'wait_for'
    model = NamedObjectModel


@App.path(model=NamedObjectCollection, path='named_objects')
def namedobject_collection_factory(request):
    storage = NamedObjectStorage(request)
    return NamedObjectCollection(request, storage)


@App.path(model=NamedObjectModel, path='named_objects/{identifier}')
def namedobject_model_factory(request, identifier):
    storage = NamedObjectStorage(request)
    return storage.get(identifier)


def test_elasticsearchstorage(es_client):
    es_client.indices.create('test-index', body={
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    })
    es_client.transport.perform_request('PUT', '/test-index/_mapping/page',
                                        body={
                                            'properties': {
                                                'title': {
                                                    'type': 'text',
                                                    'fielddata': True
                                                }
                                            }
                                        })
    client = get_client(App)
    run_jslcrud_test(client)
