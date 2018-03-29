import graphene
import graphql_jwt
from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import staff_member_required

from ...graphql.core.filters import DistinctFilterSet
from ...graphql.page.types import Page
from ...graphql.product.types import Category, Product, resolve_categories
from ...graphql.utils import get_node
from ...product import models as product_models
from .page.mutations import PageCreate, PageDelete, PageUpdate
from .page.types import resolve_all_pages
from .product.filters import ProductFilter
from .product.mutations import (
    CategoryCreateMutation, CategoryDelete, CategoryUpdateMutation,
    ProductCreateMutation, ProductDeleteMutation, ProductUpdateMutation)
from .product.types import ProductDashboard


class Query(graphene.ObjectType):
    node = graphene.Node.Field()
    debug = graphene.Field(DjangoDebug, name='__debug')

    categories = DjangoFilterConnectionField(
        Category, filterset_class=DistinctFilterSet,
        level=graphene.Argument(graphene.Int))
    category = graphene.Field(Category, id=graphene.Argument(graphene.ID))

    page = graphene.Field(Page, id=graphene.Argument(graphene.ID))
    pages = DjangoFilterConnectionField(
        Page, filterset_class=DistinctFilterSet)

    product = graphene.Field(ProductDashboard, id=graphene.Argument(graphene.ID))
    products = DjangoFilterConnectionField(
        ProductDashboard, filterset_class=ProductFilter,
        category_id=graphene.Argument(graphene.ID))

    @staff_member_required
    def resolve_category(self, info, id):
        return get_node(info, id, only_type=Category)

    @staff_member_required
    def resolve_categories(self, info, level=None, **kwargs):
        return resolve_categories(info, level)

    @staff_member_required
    def resolve_page(self, info, id):
        return get_node(info, id, only_type=Page)

    @staff_member_required
    def resolve_pages(self, info):
        return resolve_all_pages()

    @staff_member_required
    def resolve_product(self, info, id):
        return get_node(info, id, only_type=Product)

    @staff_member_required
    def resolve_products(self, info, category_id=None, **kwargs):
        if category_id is not None:
            category = get_node(info, category_id, only_type=Category)
            return product_models.Product.objects.filter(
                category=category).distinct()
        return product_models.Product.objects.all().distinct()


class Mutations(graphene.ObjectType):
    category_create = CategoryCreateMutation.Field()
    category_delete = CategoryDelete.Field()
    category_update = CategoryUpdateMutation.Field()

    page_create = PageCreate.Field()
    page_delete = PageDelete.Field()
    page_update = PageUpdate.Field()

    product_create = ProductCreateMutation.Field()
    product_delete = ProductDeleteMutation.Field()
    product_update = ProductUpdateMutation.Field()

    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(Query, Mutations)
