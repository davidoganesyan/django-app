from datetime import datetime
from django.core.management import BaseCommand
from blogapp.models import Author, Category, Tag, Article


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start creating instances")

        author_info = [
            ('Author 1', 'Bio 1'),
            ('Author 2', 'Bio 2'),
            ('Author 3', 'Bio 3'),
            ('Author 4', 'Bio 4'),
            ('Author 5', 'Bio 5'),
        ]
        category_info = [
            'category 1',
            'category 2',
            'category 3',
            'category 4',
            'category 5',
        ]
        tag_info = [
            'tag 1',
            'tag 2',
            'tag 3',
            'tag 4',
            'tag 5',
        ]
        authors = [
            Author(name=author, bio=bio)
            for author, bio in author_info
        ]
        categories = [
            Category(name=category)
            for category in category_info
        ]
        tags = [
            Tag(name=tag)
            for tag in tag_info
        ]
        articles_info = [
            ('title 1', 'content 1', datetime.now(), authors[0], categories[0],),
            ('title 2', 'content 2', datetime.now(), authors[1], categories[1],),
            ('title 3', 'content 3', datetime.now(), authors[2], categories[2],),
            ('title 4', 'content 4', datetime.now(), authors[3], categories[3],),
            ('title 5', 'content 5', datetime.now(), authors[4], categories[4],),
        ]
        articles = [
            Article(title=title, content=content, pub_date=pub_date, author=author, category=category, )
            for title, content, pub_date, author, category in articles_info
        ]
        Author.objects.bulk_create(authors)
        self.stdout.write(self.style.SUCCESS("Author creating done"))
        Category.objects.bulk_create(categories)
        self.stdout.write(self.style.SUCCESS("Category creating done"))
        Tag.objects.bulk_create(tags)
        self.stdout.write(self.style.SUCCESS("Tag creating done"))
        Article.objects.bulk_create(articles)
        self.stdout.write(self.style.SUCCESS("Article creating done"))
        self.stdout.write(self.style.SUCCESS("Some creating done"))
