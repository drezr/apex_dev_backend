import uuid

from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..misc.email_content import *
from ..models import User


class ResetPasswordView(APIView):

    permission_classes = (AllowAny, )

    def post(self, request):
        username = request.data['username'].lower()
        new_password = uuid.uuid4().hex[:8]

        user = User.objects.filter(username=username).first()

        if user:
            user.set_password(new_password)
            user.save()

            title = email_reset_password_title[request.data['lang']]
            content = email_reset_password_content[request.data['lang']] \
                        .replace('###name###', user.profile.name) \
                        .replace('###login###', username) \
                        .replace('###new_password###', new_password)

            send_mail(
                title,
                content,
                'service@apex.wf',
                [username],
                fail_silently=False
            )

            return Response({'result': 'success'})


        else:
            return Response({'result': 'error'})