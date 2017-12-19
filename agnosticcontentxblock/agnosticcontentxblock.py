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



class AgnosticContentXBlock(StudioContainerWithNestedXBlocksMixin, StudioEditableXBlockMixin, XBlock):
	"""
	TO-DO: document what your XBlock does.
	"""

	# Fields are defined on the class.  You can access them in your code as
	# self.<fieldname>.

	# TO-DO: delete count, and define your own fields.
	upvotes = Integer(help="Number of up votes", default=0,
		scope=Scope.user_state_summary)
	downvotes = Integer(help="Number of down votes", default=0,
		scope=Scope.user_state_summary)
	voted = Boolean(help="Has this student voted?", default=False,
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
	
		fragment.add_content(loader.render_template('static/html/agnosticcontentxblock.html', {
			'self': self,
			'title': self.display_name,
			'child_content': child_content,
			'upvotes':self.upvotes,
			'downvotes': self.downvotes
		}))
		
		fragment.add_css(self.resource_string("static/css/agnosticcontentxblock.css"))
		#fragment.add_javascript(self.resource_string("static/js/src/agnosticcontentxblock.js"))
		fragment.add_javascript(self.resource_string("public/js/agnosticcontentxblock.js"))
		fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/agnosticcontentxblock.js'))

		fragment.initialize_js('AgnosticContentXBlock')
		return fragment


	@XBlock.json_handler
	def vote(self, data, suffix=''):  # pylint: disable=unused-argument
		"""
		Update the vote count in response to a user action.
		"""
		# Here is where we would prevent a student from voting twice, but then
		# we couldn't click more than once in the demo!
		#
		#     if self.voted:
		#         log.error("cheater!")
		#         return
	
		if data['voteType'] not in ('up', 'down'):
			log.error('error!')
			return
		if data['voteType'] == 'up':
			self.upvotes += 1
		else:
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
