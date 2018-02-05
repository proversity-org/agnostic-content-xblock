/* Javascript for AgnosticContentXBlock. */
window.AgnosticContentXBlock = function(runtime, element, args) {
    var handlerUrl = runtime.handlerUrl(element, 'like');
    jQuery('.like', element).click(function(e) {
      jQuery.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({})
          success: function(data){
            text = data['likes']+' people liked this.'
            if(data['liked'])
              text = parseInt(data['likes']) > 1 ? 'You and '+data['likes']+' others liked this!' : 'You liked this!';
            $('.like .count', element).text(text);
          }
      });
    });
}
