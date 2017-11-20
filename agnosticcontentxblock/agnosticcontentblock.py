"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin,  StudioContainerWithNestedXBlocksMixin, NestedXBlockSpe



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
                VideoDescriptor, category='video', label=_(u"Video")
            ))
        except ImportError:
            pass

        return additional_blocks


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the AgnosticContentXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/agnosticcontentblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/agnosticcontentblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/agnosticcontentblock.js"))
        frag.initialize_js('AgnosticContentXBlock')
        return frag

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
             """<agnosticcontentblock/>
             """),
            ("Multiple AgnosticContentXBlock",
             """<vertical_demo>
                <agnosticcontentblock/>
                <agnosticcontentblock/>
                <agnosticcontentblock/>
                </vertical_demo>
             """),
        ]