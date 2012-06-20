from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.utils import shasattr

from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from Products.PloneFormGen.interfaces.actionAdapter import IPloneFormGenActionAdapter

from collective.pfg.mailchimp import MessageFactory as _

from chimpy import Connection
from chimpy.chimpy import ChimpyException
from Products.CMFCore.utils import getToolByName

from config import PROJECTNAME

from logging import getLogger
log = getLogger("collective.pfg.mailchimp")

mailchimpSubscribeAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((

    atapi.StringField('replyto_field',
        searchable=0,
        required=0,
        vocabulary='fieldsDisplayList',
        widget=atapi.SelectionWidget(
            label = _(u"Extract Subscribe Email"),
            description = _(u"""
            Choose a form field from which you wish to extract
            input for the Reply-To header. NOTE: You should
            activate e-mail address verification for the designated
            field.
            """)
            ),
        ),

    atapi.LinesField('merge_vars',
        searchable=0,
        required=0,
        widget=atapi.LinesWidget(
            label = _(u"Mailchimp merge vars"),
            description = _(u'1 per line. Variable name and fieldname, seperated by double colon. Eg. "FNAME::first-name"'),
            ),
        ),

    atapi.StringField('condition',
        searchable=0,
        required=0,
        default='#NONE#',
        vocabulary='booleanFieldsList',
        widget=atapi.SelectionWidget(
            label = _(u"Subscribe condition"),
            description = _(u"")
            ),
        ),
))

finalizeATCTSchema(mailchimpSubscribeAdapterSchema, moveDiscussion=False)


class MailchimpSubscribeAdapter(FormActionAdapter):
    """ A form action adapter that will subscribe the  form input. """
    implements(IPloneFormGenActionAdapter)
    
    schema = mailchimpSubscribeAdapterSchema
    portal_type = 'Mailchimp Subscribe Adapter'
    meta_type = 'MailchimpSubscribeAdapter'
    content_icon = 'mailaction.gif'

    security       = ClassSecurityInfo()

    security.declarePrivate('onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """
        Subscribe the 
        """
        if shasattr(self, 'condition') and \
           (REQUEST.form.get(self.condition, None) or self.condition=='#NONE#'):
            status = self.subscribe(REQUEST)

    def get_email(self, request):
        if shasattr(self, 'replyto_field'):
            return request.form.get(self.replyto_field, None)
        return ''

    def get_merge_vars(self, request):
        vars = {'FNAME':'', 'LNAME':''} #defaults
        for mapping in getattr(self, 'merge_vars'):
            key, value = mapping.split('::')
            vars[key]=value
        return vars
            
    def subscribe(self, request):
        email = self.get_email(request)
        merge_vars = self.get_merge_vars(request)
        if not (email or merge_vars):
            return
        properties = getToolByName(self, 'portal_properties')
        chimp_props = getattr(properties, 'mailchimp_properties', None)
        if chimp_props:
            api_key = getattr(chimp_props, 'mailchimp_api_key', '')
            list_id = getattr(chimp_props, 'mailchimp_list_id', '')
            try:
                chimp = Connection(api_key)
                chimp.list_subscribe(
                    id=list_id,
                    email_address=email,
                    merge_vars=merge_vars,
                    double_optin=False)
            except ChimpyException, e:
                log.warn("While trying to subscribe %s. Mailchimp replied: %s" % (
                    email, e.message))
                if 'already subscribed' in e.message:
                    pass # that's fine for our purposes
                else:
                    raise # must be a real problem

    def booleanFieldsList(self):
        """ returns display list of fields with simple values """
        return self.fgFieldsDisplayList(
            withNone=False,
            objTypes=(
                'FormBooleanField',
                )
            )

    def fieldsDisplayList(self):
        """ returns display list of fields with simple values """

        return self.fgFieldsDisplayList(
            withNone=True,
            noneValue='#NONE#',
            objTypes=(
                'FormSelectionField',
                'FormStringField',
                )
            )

atapi.registerType(MailchimpSubscribeAdapter, PROJECTNAME)
