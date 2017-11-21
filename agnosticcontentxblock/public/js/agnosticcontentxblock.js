/* Javascript for AgnosticContentXBlock. */
function AgnosticContentXBlock(runtime, element) {

    function updateCount(result) {
        $('.count', element).text(result.count);
    }
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
