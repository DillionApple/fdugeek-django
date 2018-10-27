from django.urls import path

from task import views

urlpatterns = [
    path("list/", views.get_task_list),
    path("detail/", views.get_task),
    path("applications/", views.get_task_applications),
    path("new/", views.create_task),
    path("delete/", views.delete_task),
    path("change/", views.change_task),
    path("finish/", views.finish_task),
    path("apply/", views.apply_for_task),
    path("quit/", views.quit_task),
    path("make_comment/", views.make_comment),
    path("comments/", views.get_comments),
    path("user/applications/", views.get_user_applications),
    path("user/published_tasks/", views.get_published_tasks),
    path("user/if_applied_task/", views.get_if_user_applied_task),
]
