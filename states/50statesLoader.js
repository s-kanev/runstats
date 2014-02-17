(function() {
    
    var mapBloggerPath = "http://s-kanev.github.io/runstats/states/";
    //var mapBloggerPath = "http://localhost:8000/"
    var RequireJS = mapBloggerPath + "require.js";
    var mapBloggerCSS = mapBloggerPath + "50states.css";

    /* Append CSS to head */
    var cssElem = document.createElement('link');
    cssElem.rel = 'stylesheet';
    cssElem.type = 'text/css';
    cssElem.href = mapBloggerCSS;
    var theHead = document.getElementsByTagName('head')[0];
    theHead.appendChild(cssElem);

    /* Append requireJS script to deal with all dependences and register onload */
    var elem = document.createElement('script');
    elem.onload = function() {
        requirejs.config({
            "paths": {
              "d3": "http://d3js.org/d3.v3.min",
              "topojson": "http://d3js.org/topojson.v1.min",
              "queue": "http://d3js.org/queue.v1.min",
              "d3.tip": mapBloggerPath + "d3.tip",
              "50states" : mapBloggerPath + "50states"
            }
        });

        /* Actually load the main map module */
        requirejs(["50states"]);
    }
    elem.src = RequireJS;
    var theBody = document.getElementsByTagName('body')[0];
    theBody.appendChild(elem);
})();
