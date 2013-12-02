function drawStatesMap() {

  var statesFile = "https://dl.dropboxusercontent.com/s/t4h6uol5jgudo3e/us.json";
  var statesNamesFile = "https://dl.dropboxusercontent.com/s/h8pts8fkzgarajg/state_names.json";

  function nameByID(id, names) {
    for (i in names) {
      if (names[i].id == id)
        return names[i];
    }
    return null;
  }
  function ranByState(state, ran) {
    for (i in ran) {
      if (ran[i].state == state)
        return ran[i];
    }
    return null;
  }
  function ranByID(id, names, ran) {
    var state = nameByID(id, names);
    if (state == null)
      return false;
    return ranByState(state.state, ran);
  }
  function hasRun(id, names, ran) {
    var state = nameByID(id, names);
    if (state == null)
      return false;
    return (ranByState(state.state, ran) != null);
  }

  var path = d3.geo.path();

  var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d, names, ran) {
      return "<span class='tip-heading'>" + nameByID(d.id, names).name +"</span> <br/> <br/> "+ ranByID(d.id, names, ran).text;
    })

  var container = d3.select(".states-container");
  var dataFile = container.attr("data");

  var svg = container.append("svg")
      .attr("id", "map")
      .attr("viewBox", "0 0 960 500")
      .attr("width", "100%")
      .attr("preserveAspectRatio", "none");

  svg.call(tip);

  function json(path, callback) {
    d3.json(path, function(json_) {
      json_ ? callback(null, json_) : callback("error", null);
    });
  }

  queue()
    .defer(json, statesFile)
    .defer(json, statesNamesFile)
    .defer(json, dataFile)
    .await(function(error, us, names, ran) {
      if (error) console.error(error)

      svg.append("path")
          .datum(topojson.feature(us, us.objects.land))
          .attr("class", "land")
          .attr("d", path);

      svg.selectAll(".state")
          .data(topojson.feature(us, us.objects.states).features)
          .enter().append("path")
          .attr("class", function(d) {
            ran_ = ranByID(d.id, names, ran);
            if (ran_ == null) return "state";
            if (ran_.text == "TBD") return "state tbd";
            return "state ran";
          })
          .attr("d", path)
          .on('mouseover', function(d) {
            if (hasRun(d.id, names, ran))
              tip.show(d, names, ran);
          })
          .on('mouseout', function(d) {
            if (hasRun(d.id, names, ran))
              tip.hide(d, names, ran);
          });
    });

}
