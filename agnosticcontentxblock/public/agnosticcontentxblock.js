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
    var handlerUrl = runtime.handlerUrl(element, 'increment_count');

    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
