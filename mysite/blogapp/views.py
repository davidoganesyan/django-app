from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from blogapp.models import Article


class ArticleListView(ListView):
    queryset = (
        Article.objects
        # .defer("content")
        .select_related("author")
        .select_related("category")
        .prefetch_related("tags")
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and additions blog articles"
    link = reverse_lazy("blogapp:articles_list")

    def items(self):
        return (
            Article.objects
            .select_related("author")
            .select_related("category")
            .prefetch_related("tags")[:3]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:100]

    # def item_link(self, item: Article):
    #     return reverse("blogapp:article", kwargs={"pk": item.pk})
