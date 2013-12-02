(function() {
    
    var mapBloggerPath = "https://raw.github.com/s-kanev/runstats/master/states/50states.js";

    // Initialize the load the main script.
    try {
        drawStatesMap();
    } catch(e) {
        var scriptId = 'mapPrinter';
        if (document.getElementById(scriptId) === null) {
            var elem = document.createElement('SCRIPT');
            elem.id = scriptId;
            elem.onload = function() {
              drawStatesMap();
            }
            elem.src = mapBloggerPath;
            var theBody = document.getElementsByTagName('body')[0];
            theBody.appendChild(elem);
        }
    }
})();
