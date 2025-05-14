import graphene
from graphene_django import relay, DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from contenido.models import Books, Genre


class GenreNode(DjangoObjectType):
    class Meta:
        model = Genre
        filter_fields = ("name", "book")
        interfaces = (relay.Node, )


class BooksNode(DjangoObjectType):
    class Meta:
        model = Books
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'autor': ['exact', 'icontains'],
            'genre': ['exact'],
            'genrer__name': ['exact']
        }
        interfaces = (relay.Node)


class Query(graphene.ObjectType):
    book = relay.Node.Field(BooksNode)
    all_books = DjangoFilterConnectionField(BooksNode)
    genre = relay.Node.Field(GenreNode)
    genre_by_name = graphene.Field(
        GenreNode, name=graphene.String(required=True))
    all_genre = DjangoFilterConnectionField(GenreNode)

    def resolve_all_books(root, info):
        return Books.objects.select_related("genre").all()

    def resolve_genre_by_name(root, info, name):
        try:
            return Genre.objects.get(name=name)
        except Genre.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
