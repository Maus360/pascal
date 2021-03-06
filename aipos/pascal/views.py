from django.shortcuts import render
from django.views import generic
from .models import Blog, Author
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from datetime import date
import logging

logger = logging.getLogger("pascal")


def index(request):
    """
    View function for home page of site.
    """
    # Render the HTML template index.html
    return render(request, "index.html")


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("index")
    template_name = "registration/signup.html"


class BlogListView(generic.ListView):
    """
    Generic class-based view for a list of all blogs.
    """

    model = Blog
    paginate_by = 5


class BlogListbyAuthorView(generic.ListView):
    """
    Generic class-based view for a list of blogs posted by a particular BlogAuthor.
    """

    model = Blog
    paginate_by = 5
    template_name = "pascal/blog_list_by_author.html"

    def get_queryset(self):
        """
        Return list of Blog objects created by BlogAuthor (author id specified in URL)
        """
        id = self.kwargs["pk"]
        target_author = get_object_or_404(Author, pk=id)
        return Blog.objects.filter(author=target_author)

    def get_context_data(self, **kwargs):
        """
        Add BlogAuthor to context so they can be displayed in the template
        """
        # Call the base implementation first to get a context
        context = super(BlogListbyAuthorView, self).get_context_data(**kwargs)
        # Get the blogger object from the "pk" URL parameter and add it to the context
        context["blogger"] = get_object_or_404(Author, pk=self.kwargs["pk"])
        return context


class BlogDetailView(generic.DetailView):
    """
    Generic class-based detail view for a blog.
    """

    model = Blog


class BlogDeleteView(generic.DeleteView):
    model = Blog
    success_url = reverse_lazy("blogs")

    def get_queryset(self):
        id_ = self.kwargs["pk"]
        self.queryset = Blog.objects.filter(pk=id_)
        return self.queryset

    def get(self, request, *args, **kwargs):
        blog = self.get_queryset().first()
        if request.user == blog.author.user:
            logger.info("user (%s) want to delete blog (%s)", request.user, blog)
            return super(BlogDeleteView, self).get(request, *args, **kwargs)
        else:
            logger.info(
                "user (%s) want to delete blog (%s) by author (%s)",
                request.user,
                blog,
                blog.author.user,
            )
            return HttpResponseRedirect(
                reverse("blog-detail", kwargs={"pk": self.kwargs["pk"]})
            )

    def post(self, request, *args, **kwargs):
        self.items_to_delete = self.request.POST.getlist("itemsToDelete")
        if self.request.POST.get("confirm"):
            logger.info("user (%s) delete blog (%s)", request.user, self.get_queryset())
            # when confirmation page has been displayed and confirm button pressed
            queryset = self.get_queryset()
            queryset.delete()  # deleting on the queryset is more efficient than on the model object
            return HttpResponseRedirect(self.success_url)
        elif self.request.POST.get("cancel"):
            logger.info(
                "user (%s) not delete blog (%s)", request.user, self.get_queryset()
            )
            # when confirmation page has been displayed and cancel button pressed
            return HttpResponseRedirect(self.success_url)
        else:
            # when data is coming from the form which lists all items
            return self.get(self, *args, **kwargs)


class BlogUpdateView(generic.UpdateView):
    model = Blog
    fields = ["name", "description"]
    success_url = reverse_lazy("blogs")

    def get_queryset(self):
        id_ = self.kwargs["pk"]
        self.queryset = Blog.objects.filter(pk=id_)
        return self.queryset

    def get(self, request, *args, **kwargs):
        blog = self.get_queryset().first()
        if request.user == blog.author.user:
            logger.info("user (%s) want to update blog (%s)", request.user, blog)
            return super(BlogUpdateView, self).get(request, *args, **kwargs)
        else:
            logger.info(
                "user (%s) want to update blog (%s) by author (%s)",
                request.user,
                blog,
                blog.author.user,
            )
            return HttpResponseRedirect(
                reverse("blog-detail", kwargs={"pk": self.kwargs["pk"]})
            )

    def form_valid(self, form):
        form.instance.post_date = date.today()
        return super().form_valid(form)


class BlogCreateView(generic.CreateView):
    model = Blog
    fields = ["name", "description"]
    success_url = reverse_lazy("blogs")
    template_name = "pascal/blog_form_create.html"

    def get_success_url(self):
        return reverse("blogs")

    def form_valid(self, form):
        user = self.request.user
        target_author = Author.objects.filter(user=user).first()
        if target_author is None:
            logger.info("register new author by user (%s)", self.request.user)
            form.instance.author = Author.objects.create(user=self.request.user, bio="")
            logger.info(
                "user (%s) create blog (%s)", self.request.user, form.instance.name
            )
        else:
            logger.info(
                "user (%s) create blog (%s)", self.request.user, form.instance.name
            )
            form.instance.author = target_author
        form.instance.post_date = date.today()
        return super().form_valid(form)


class BloggerListView(generic.ListView):
    """
    Generic class-based view for a list of bloggers.
    """

    model = Author
    paginate_by = 5
