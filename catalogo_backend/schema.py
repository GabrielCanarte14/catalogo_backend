import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload

from contenido.models import Books, Genre


class GenreNode(DjangoObjectType):
    class Meta:
        model = Genre
        filter_fields = ("name", "book")
        interfaces = (relay.Node, )


class BooksNode(DjangoObjectType):
    cover_url = graphene.String()

    class Meta:
        model = Books
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'autor': ['exact', 'icontains'],
            'genre': ['exact'],
            'genre__name': ['exact'],  # corregido el typo
        }
        interfaces = (relay.Node, )

    def resolve_cover_url(self, info):
        request = info.context
        if self.cover:
            return request.build_absolute_uri(self.cover.url)
        return None

class CreateBook(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        autor = graphene.String(required=True)
        isbn = graphene.String(required=False)
        editorial = graphene.String(required=False)
        genre_id = graphene.ID(required=True)
        pub_date = graphene.DateTime(required=True)
        cover = Upload(required=False)

    book = graphene.Field(BooksNode)

    def mutate(self, info, name, autor, genre_id, isbn="", editorial="", cover=None, pub_date=None):
        genre = relay.Node.get_node_from_global_id(info, genre_id, only_type=GenreNode)
        if genre is None:
            raise Exception("Género no encontrado")

        book = Books.objects.create(
            name=name,
            autor=autor,
            isbn=isbn,
            editorial=editorial,
            genre=genre,
            pub_date=pub_date,
            cover=cover 
        )
        return CreateBook(book=book)


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

class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

