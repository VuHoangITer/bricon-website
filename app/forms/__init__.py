from app.forms.auth import LoginForm
from app.forms.user import UserForm, RoleForm, PermissionForm
from app.forms.content import BlogForm, FAQForm
from app.forms.product import CategoryForm, ProductForm
from app.forms.media import BannerForm, MediaSEOForm, ProjectForm
from app.forms.job import JobForm
from app.forms.contact import ContactForm
from app.forms.settings import SettingsForm
from app.forms.quiz import QuizForm, QuestionForm, QuizStartForm
from app.forms.distributor import DistributorForm
from app.forms.popup import PopupForm

__all__ = [
    'LoginForm',
    'UserForm', 'RoleForm', 'PermissionForm',
    'BlogForm', 'FAQForm',
    'CategoryForm', 'ProductForm',
    'BannerForm', 'MediaSEOForm', 'ProjectForm',
    'JobForm',
    'ContactForm',
    'SettingsForm',
    'QuizForm', 'QuestionForm', 'QuizStartForm',
    'DistributorForm',
    'PopupForm'
]