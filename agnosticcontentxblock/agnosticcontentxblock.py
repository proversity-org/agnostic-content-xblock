"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from xblockutils.resources import ResourceLoader

import logging
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin,  StudioContainerWithNestedXBlocksMixin, NestedXBlockSpec
logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


@XBlock.needs('user', 'bookmarks')
class AgnosticContentXBlock(StudioContainerWithNestedXBlocksMixin, StudioEditableXBlockMixin, XBlock):
	"""
	TO-DO: document what your XBlock does.
	"""

	# Fields are defined on the class.  You can access them in your code as
	# self.<fieldname>.

	# TO-DO: delete count, and define your own fields.

	block_id = String(
		display_name='ID',
		help='The ID of the Free Text Response XBlock',
		scope=Scope.settings,
	)

	upvotes = Integer(help="Number of total up votes", default=0,
		scope=Scope.user_state_summary)
	downvotes = Integer(help="Number of total down votes", default=0,
		scope=Scope.user_state_summary)

	upvoted = Boolean(help="Has this student voted up?", default=False,
		scope=Scope.user_state)

	downvoted = Boolean(help="Has this student voted down?", default=False,
		scope=Scope.user_state)

	count = Integer(
		default=0, scope=Scope.user_state,
		help="A simple counter, to show something happening",
	)

	display_name = String(
		display_name="Title (Display name)",
		help="Title to display",
		default="Agnostic Content Block",
		scope=Scope.settings
	)

	use_latex_compiler = Boolean(
		help="Enable LaTeX templates?",
		default=False,
		scope=Scope.settings
	)

	has_children = True
	#show_in_read_only_mode = True
	editable_fields = ('display_name',)

	@property
	def allowed_nested_blocks(self):
		"""
		Returns a list of allowed nested XBlocks. Each item can be either
		* An XBlock class
		* A NestedXBlockSpec

		If XBlock class is used it is assumed that this XBlock is enabled and allows multiple instances.
		NestedXBlockSpec allows explicitly setting disabled/enabled state, disabled reason (if any) and single/multiple
		instances
		"""
		additional_blocks = []
		try:
			from xmodule.video_module.video_module import VideoDescriptor
			additional_blocks.append(NestedXBlockSpec(
				VideoDescriptor, category='video', label=u"Video"
			))
		except ImportError:
			pass
		try:
			from xmodule.html_module import HtmlDescriptor
			additional_blocks.append(NestedXBlockSpec(
				HtmlDescriptor, category='html', label=u"HTML"
			))
		except ImportError:
			pass
		try:
			from xmodule.capa_module import CapaDescriptor
			additional_blocks.append(NestedXBlockSpec(
				CapaDescriptor, category='problem', label=u"CapaProblem"
			))
		except ImportError:
			pass
		try:
			from pdf.pdf import PdfBlock
			additional_blocks.append(NestedXBlockSpec(
				PdfBlock, category='pdf', label=u"PDF"
			))
		except ImportError:
			logger.warn('Could not import PdfBlock')
			pass
		try:
			from google_drive.google_docs import GoogleDocumentBlock
			additional_blocks.append(NestedXBlockSpec(
				GoogleDocumentBlock, category='google-document', label=u"Google-doc"
			))
		except ImportError:
			pass
		try:
			from xblock_discussion import DiscussionXBlock
			additional_blocks.append(NestedXBlockSpec(
				DiscussionXBlock, category='discussion', label=u'Discussion'
			))
		except ImportError:
			pass
		try:
			from bibblio import BibblioXBlock
			additional_blocks.append(NestedXBlockSpec(
				BibblioXBlock, category='bibblio', label=u'Bibblio'
			))
		except ImportError:
			pass


		return additional_blocks


	def resource_string(self, path):
		"""Handy helper for getting resources from our kit."""
		data = pkg_resources.resource_string(__name__, path)
		return data.decode("utf8")

	@XBlock.supports("multi_device") # mobile friendly
	def student_view(self, context=None):
		"""
		The primary view of the AgnosticContentXBlock, shown to students
		when viewing courses.
		"""
		fragment = Fragment()
		child_content = u""
		for child_id in self.children:
			try:
				child = self.runtime.get_block(child_id)
				child_fragment = child.render('student_view', context)
				fragment.add_frag_resources(child_fragment)
				child_content += child_fragment.content
			except: # child should not be None but it can happen due to bugs or permission issues
				child_content += u"<p>[{}]</p>".format(u"Error: Unable to load child component.")

		bookmarks_service = self.runtime.service(self, 'bookmarks')
		user_service = self.runtime.service(self, 'user')
		username = user_service.get_current_user().opt_attrs['edx-platform.username']

		fragment.add_content(loader.render_template('static/html/agnosticcontentxblock.html', {
			'self': self,
			'title': self.display_name,
			'child_content': child_content,
			'upvotes':self.upvotes,
			'downvotes': self.downvotes,
			'show_bookmark_button': True,
			'is_bookmarked': bookmarks_service.is_bookmarked(usage_key=self.location),
			'bookmark_id': u"{},{}".format(username, unicode(self.location)),
			'block_usage_id': unicode(self.location.block_id)
		}))

		fragment.add_css(self.resource_string("static/css/agnosticcontentxblock.css"))
		fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/agnosticcontentxblock.js'))
		fragment.initialize_js('AgnosticContentXBlock')

		fragment.initialize_js('VerticalStudentView', { 'selector':'#bookmark-'+unicode(self.location.block_id) })

		return fragment


	@XBlock.json_handler
	def vote(self, data, suffix=''):  # pylint: disable=unused-argument
		"""exi
		Update the vote count in response to a user action.
		"""
		# Here is where we would prevent a student from voting twice, but then
		# we couldn't click more than once in the demo!
		#
		if self.upvoted or self.downvoted:
		   logger.error("A user may not have more than one opportunity to vote")
		   return

		if data['voteType'] not in ('up', 'down'):
			logger.error('error!')
			return
		if data['voteType'] == 'up':
			self.upvoted = True
			self.upvotes += 1
		else:
			self.downvoted = True
			self.downvotes += 1
		self.voted = True
		return {'up': self.upvotes, 'down': self.downvotes}

	# TO-DO: change this to create the scenarios you'd like to see in the
	# workbench while developing your XBlock.
	@staticmethod
	def workbench_scenarios():
		"""A canned scenario for display in the workbench."""
		return [
			("AgnosticContentXBlock",
			 """<agnosticcontentxblock/>
			 """),
			("Multiple AgnosticContentXBlock",
			 """<vertical_demo>
				<agnosticcontentxblock/>
				<agnosticcontentxblock/>
				<agnosticcontentxblock/>
				</vertical_demo>
			 """),
		]
