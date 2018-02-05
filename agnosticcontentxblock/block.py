"""TO-DO: Write a description of what this XBlock is."""

import logging
import pkg_resources

from datetime import datetime
from xmodule.modulestore.django import modulestore
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean, DateTime
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin,  StudioContainerWithNestedXBlocksMixin, NestedXBlockSpec
from xblockutils.resources import ResourceLoader
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


@XBlock.needs('user', 'bookmarks')
class AgnosticContentXBlock(StudioContainerWithNestedXBlocksMixin, StudioEditableXBlockMixin, XBlock):
	"""
	TO-DO: document what your XBlock does.
	"""

	# Fields are defined on the class.  You can access them in your code as
	# self.<fieldname>.

	block_id = String(
		display_name='ID',
		help='The ID of the Agnostic Content XBlock',
		scope=Scope.settings,
	)

	likes = Integer(
		help="Number of total likes",
		default=0,
		scope=Scope.user_state_summary
	)

	liked = Boolean(
		help="Has this student liked this yet?",
		default=False,
		scope=Scope.user_state
	)

	views = Integer(
		help="How many times has this student seen this?",
		default=0,
		scope=Scope.user_state_summary
	)

	last_viewed = DateTime(
		help="When did this student last see this?",
		default=None,
		scope=Scope.user_state
	)

	completed = Boolean(
		help="Has this student completed this?",
		default=False,
		scope=Scope.user_state
	)

	display_name = String(
		display_name="Title (Display name)",
		help="Title to display",
		default="Agnostic Content Block",
		scope=Scope.settings
	)

	content_item_id = String(
		display_name='Content Item ID',
		help='The Bibblio Content Item ID represented',
		default="",
		scope=Scope.settings,
	)

	use_latex_compiler = Boolean(
		help="Enable LaTeX templates?",
		default=False,
		scope=Scope.settings
	)

	editable_fields = ('display_name','content_item_id',)
	has_children = True

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
			'liked': self.liked,
			'likes': self.likes,
			'show_bookmark_button': True,
			'is_bookmarked': bookmarks_service.is_bookmarked(usage_key=self.location),
			'bookmark_id': u"{},{}".format(username, unicode(self.location)),
			'block_usage_id': unicode(self.location.block_id)
		}))

		fragment.add_css(self.resource_string("static/css/agnosticcontentxblock.css"))
		fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/agnosticcontentxblock.js'))
		fragment.initialize_js('VerticalStudentView', { 'selector':'#bookmark-'+unicode(self.location.block_id) })
		fragment.initialize_js('AgnosticContentXBlock')

		self.last_viewed = datetime.now()
		self.views = self.views+1

		return fragment


	@XBlock.json_handler
	def like(self, data, suffix=''):  # pylint: disable=unused-argument
		"""
		Update the likes count in response to a user action.
		"""
		# Here is where we would prevent a student from voting twice, but then
		# we couldn't click more than once in the demo!

		if self.liked:
			self.liked = False
			self.likes -= 1
		elif not self.liked:
			self.liked = True
			self.likes += 1

		return { 'likes': self.likes, 'liked': self.liked }


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
