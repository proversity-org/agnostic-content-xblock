/* Javascript for AgnosticContentXBlock. */
function AgnosticContentXBlock(runtime, element) {

    function updateVotes(votes) {
        $('.upvote .count', element).text(votes.up);
        $('.downvote .count', element).text(votes.down);
    }

    var handlerUrl = runtime.handlerUrl(element, 'vote');

    $('.upvote', element).click(function(eventObject) {
      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({voteType: 'up'}),
          success: updateVotes
      });
    });

    $('.downvote', element).click(function(eventObject) {
      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({voteType: 'down'}),
          success: updateVotes
      });
    });

    var children = runtime.children(element);
   
    return {

        initChildren: function(options) {
            for (var i=0; i < children.length; i++) {
                var child = children[i];
                console.log('Hi', child)
                callIfExists(child, 'init', options);
            }
        },

    };
}
