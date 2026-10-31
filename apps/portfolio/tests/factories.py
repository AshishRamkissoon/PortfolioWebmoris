import factory

from apps.core.placeholders import placeholder_image
from apps.portfolio.models import Project, ProjectCategory, ProjectImage, ProjectMetric


def _image(name="test.png"):
    return placeholder_image("test", size=(80, 60), name=name)


class ProjectCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectCategory

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Project {n}")
    slug = factory.Sequence(lambda n: f"project-{n}")
    client = "Test Client"
    year = 2026
    short_description = "A short description."
    challenge = "The challenge."
    solution = "The solution."
    cover_image = factory.LazyFunction(_image)
    is_published = True

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if create and extracted:
            self.categories.set(extracted)


class ProjectImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectImage

    project = factory.SubFactory(ProjectFactory)
    image = factory.LazyFunction(_image)


class ProjectMetricFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectMetric

    project = factory.SubFactory(ProjectFactory)
    value = "+50%"
    label = "traffic"
