import enum
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.auto_raise import auto_raise
from adh6.constants import MembershipDuration
from adh6.member.interfaces.notification_repository import NotificationRepository

class NotificationManager:
    def __init__(self, notification_repository: NotificationRepository) -> None:
        self.notification_repository = notification_repository

    @log_call
    @auto_raise
    def send(self, ctx, template_id :str, member_email :str, **kwargs):

        self.notification_repository.send()
        '''        
        server = smtplib.SMTP('192.168.102.18', 25)
        msg = EmailMessage()
        msg['Subject'] = "COTISATION MiNET / MiNET SUBSCRIBTION :"
        msg['From'] = "no-reply@minet.net"
        msg['To'] = member_email
        msg.set_content("""\
        -- ENGLISH VERSION BELOW --

Bonjour/Bonsoir,

Ta demande de (re)cotisation de {subscription_duration.value} mois a bien été prise en compte. Elle expirera le {subscription_end}.

Pour configurer tes appareils, nous t'invitons à te rendre sur le site https://minet.net/fr/tutoriels.html qui t'explique comment configurer tes appareils. En cas de problème, tu peux nous écrire sur https://tickets.minet.net, et nous t'aiderons à régler tes problèmes, ou bien passer au local associatif dans le foyer, aux horaires de permanence (du lundi au vendredi de 18h à 19h30).

Cordialement,
L'équipe MiNET.

----

Hello/Good evening,

Your request for (re-)contribution of {subscription_duration.value} months has been taken into account. It will expire on {subscription_end}.

To configure your devices, we invite you to visit https://minet.net/en/tutoriels.html which explains how to configure your devices. In case of problem, you can write to us on https://tickets.minet.net/, and we will help you to solve your problems, or come to the association's office in the foyer, during office hours (Monday to Friday from 6pm to 7:30pm).

Best regard,
MiNET Team.
        """)
        server.send_message(msg)
'''