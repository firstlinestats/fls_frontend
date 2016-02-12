var CreateHistorical = function createHistorical(divid, data, tableid) {

  var parseDate = d3.time.format("%Y-%m-%d").parse;

  for (d in data) {
    data[d].forEach(function(d) {
      d.date = parseDate(d.date);
    });
  }

  var margin = {top: 20, right: 80, bottom: 30, left: 50},
      width = $(tableid).width() - margin.left - margin.right,
      height = $(tableid).height() - margin.top - margin.bottom;

  var x = d3.time.scale()
      .range([0, width]);

  var y = d3.scale.linear()
      .range([height, 0]);

  var color = d3.scale.category10();

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .tickFormat(d3.time.format("%b %d"))
      .ticks(5);

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(5);

  var line = d3.svg.line()
      .interpolate("basis")
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d.points); });

  var svg = d3.select(divid).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var minDate = maxDate = null;
  var minPoints = 0;
  var maxPoints = 0;
  for (d in data) {
    minDate = data[d][0]["date"];
    maxDate = data[d][data[d].length - 1]["date"];
    for (var i=0; i<data[d].length; i++) {
      var point = data[d][i].points;
      if (point > maxPoints)
        maxPoints = point;
    }
  }

  x.domain([minDate, maxDate]);

  y.domain([minPoints, maxPoints]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Points");

  for (d in data) {
    svg.append("path")
        .datum(data[d])
        .attr("class", "line")
        .attr("d", line)
        .attr("id", d.replace(" ", "") + "line")
        .style("stroke", function(v) {
          return get_color(d, false);
        });
    svg.append("path")
        .datum(data[d])
        .attr("class", "innerline")
        .attr("d", line)
        .attr("id", d.replace(" ", "") + "innerline")
        .style("stroke", function(v) {
          return get_color(d, true);
        })
  }

  var legendRectSize = 10,
      legendSpacing = 5;
  var box = svg.append("rect")
    .attr('width', 110)
    .attr('height', (Object.keys(data).length + 2) * (legendSpacing + legendRectSize))
    .attr('transform', "translate(" + (margin.left - legendRectSize) + ", " + legendRectSize + ")")
    .attr('fill', 'none')
    .attr('stroke', 'black')
  var boxtext = svg.append("text")
    .attr('x', 55)
    .attr('y', (Object.keys(data).length + 2) * (legendSpacing + legendRectSize))
    .style('font-size', '12px')
    .text('Click to Toggle')
  var legend = svg.append("g")
      .selectAll("g")
      .data(Object.keys(data))
      .enter()
      .append('g')
        .attr('class', 'legend')
        .attr('transform', function(d, i) {
          var height = legendRectSize;
          var x = margin.left;
          var y = i * height + i * legendSpacing + legendRectSize + 10;
          return 'translate(' + x + ',' + y + ')';
      });
  legend.append('rect')
      .attr('width', legendRectSize)
      .attr('height', legendRectSize)
      .style('fill', function(d) { return get_color(d, true); })
      .attr('cursor', 'pointer')
      .attr('id', function(d) {
          return d.replace(" ", "") + "legendrect";
      })
      .attr("onclick", function(d) {
          return "toggleLine(\"" + d.replace(" ", "") + "\");";
      })
      .style('stroke', function(d) { return get_color(d, false); });
   
  legend.append('text')
      .attr('x', legendRectSize + legendSpacing)
      .attr('y', legendRectSize - legendSpacing + (legendRectSize / 2))
      .attr('cursor', 'pointer')
      .attr('id', function(d) {
          return d.replace(" ", "") + "legendtext";
      })
      .attr("onclick", function(d) {
          return "toggleLine(\"" + d.replace(" ", "") + "\");";
      })
      .text(function(d) { return d; });



  svg.append("text")
    .attr("x", width - margin.right - 50)
    .attr("y", height - margin.bottom)
    .attr("text-anchor", "right")
    .style("font-size", "14px")
    .style("fill", "grey")
    .text("firstlinestats.com")

};

function toggleLine(teamname) {
    var id = "#" + teamname + "line";
    var id2 = "#" + teamname + "innerline";
    var lid = "#" + teamname + "legendtext";
    var lid2 = "#" + teamname + "legendrect";
    $(id).toggleClass("invisible");
    $(id2).toggleClass("invisible");
    $(lid).toggleClass("opacityfifty");
    $(lid2).toggleClass("opacityfifty");
}