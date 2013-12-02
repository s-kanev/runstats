(function() {
    
    var mapBloggerPath = "https://raw.github.com/s-kanev/runstats/master/states/";
    //var mapBloggerPath = "http://localhost:8088/"
    var mapBloggerJS = mapBloggerPath + "50states.js";
    var mapBloggerCSS = mapBloggerPath + "50states.css";
    var d3TipJS = "http://labratrevenge.com/d3-tip/javascripts/d3.tip.min.js";

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
            var elem = document.createElement('script');
            elem.id = scriptId;
            elem.onload = function() {
                /* Ok, I'm sure this can generalize. */
                var newElem = document.createElement('script');
                newElem.id = "mapPrinter2";
                newElem.onload = function() {
                    drawStatesMap();
                }
                newElem.src = mapBloggerJS;
                var theBody2 = document.getElementsByTagName('body')[0];
                theBody2.appendChild(newElem);
            }
            elem.src = d3TipJS;
            var theBody = document.getElementsByTagName('body')[0];
            theBody.appendChild(elem);
        }
    }
})();
