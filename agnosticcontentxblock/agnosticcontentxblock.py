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
			from recap import RecapXBlock
			additional_blocks.append(NestedXBlockSpec(
				RecapXBlock, category='recap', label=u"Recap"
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
		}))
		
		fragment.add_css(self.resource_string("static/css/agnosticcontentxblock.css"))
		#fragment.add_javascript(self.resource_string("static/js/src/agnosticcontentxblock.js"))
		fragment.add_javascript(self.resource_string("public/js/agnosticcontentxblock.js"))
		fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/agnosticcontentxblock.js'))

		fragment.initialize_js('AgnosticContentXBlock')
		return fragment

	# TO-DO: change this handler to perform your own actions.  You may need more
	# than one handler, or you may not need any handlers at all.
	@XBlock.json_handler
	def increment_count(self, data, suffix=''):
		"""
		An example handler, which increments the data.
		"""
		# Just to show data coming in...
		assert data['hello'] == 'world'

		self.count += 1
		return {"count": self.count}

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
