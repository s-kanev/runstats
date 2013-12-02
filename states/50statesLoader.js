(function() {
    
    var mapBloggerPath = "https://raw.github.com/s-kanev/runstats/master/states/";
    //var mapBloggerPath = "http://localhost:8088/"
    var mapBloggerJS = mapBloggerPath + "50states.js";
    var mapBloggerCSS = mapBloggerPath + "50states.css";

    // Initialize the main script.
    try {
        drawStatesMap();
    } catch(e) {
        var scriptId = 'mapPrinter';
        if (document.getElementById(scriptId) === null) {
            /* Append CSS to head */
            var cssElem = document.createElement('link');
            cssElem.rel = 'stylesheet';
            cssElem.type = 'text/css';
            cssElem.href = mapBloggerCSS;
            var theHead = document.getElementsByTagName('head')[0];
            theHead.appendChild(cssElem);

            /* Append main script and register onload */
            var elem = document.createElement('SCRIPT');
            elem.id = scriptId;
            elem.onload = function() {
              drawStatesMap();
            }
            elem.src = mapBloggerJS;
            var theBody = document.getElementsByTagName('body')[0];
            theBody.appendChild(elem);
        }
    }
})();
