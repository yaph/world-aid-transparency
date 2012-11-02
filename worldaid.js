(function() {

var width = 720,
  height = 540,
  centered,
  geocountries,
  proj = d3.geo.equirectangular().scale(1).translate([0, 0]),
//  color = d3.scale.category20();

  color = function(d) {return '#000'};

var projection = d3.geo.mercator()
  .scale(width)
  .translate([0, 0]);

var path = d3.geo.path()
  .projection(projection);

var tf = function() {
  return 'translate(' + width / 2 + ',' + height / 2 + ')'
};

var svg = d3.select('#map').append('svg')
  .attr('width', width)
  .attr('height', height);

svg.append('rect')
  .attr('class', 'background')
  .attr('width', width)
  .attr('height', height);

var gcountries = svg.append('g')
  .attr('transform', tf)
  .append('g')
    .attr('id', 'countries');

var glinks = svg.append('g')
  .attr('transform', tf)
  .append('g')
    .attr('id', 'links');

var garcs = svg.append('g')
  .attr('transform', tf)
  .attr('id', 'arcs');

var arc = d3.geo.greatArc()
  .precision(1);

var centroid = function(d) {
  return path.centroid(d.geometry)
};

var spain = [-3.43, 40.23];
var mexico = [-99.8, 19.26];
var links = [{
  'source': spain,
  'target': mexico
  }, {
  'source': mexico,
  'target': spain
}];

var click = function(d) {
  console.log(d);
}

var linkcoords = function(d) {
  d.source = capitals[d.source].coords;
  d.target = capitals[d.target].coords;
  return d;
};

// use min and max of total
var scalelinks = d3.scale.sqrt().domain([-10000000,10000000]);

var drawlinks = function(data) {
  garcs.selectAll('path')
    .data(data.filter(function(d){
      return ('undefined' !== typeof capitals[d.source]
        && 'undefined' !== typeof capitals[d.target]
      ) ? true : false
    }).slice(1, 100))
    .enter().append('path')
      .style('stroke-width', function(d) {console.log(d.usdollars); return scalelinks(d.usdollars) })
      .style('stroke', function(d) {return color(d.source)})
      .style('fill', 'none')
      .style('opacity', .5)
      .attr('d', function(d) {return path(arc(linkcoords(d)))});
}

drawlinks(donations);

d3.json('world-countries.json', function(error, json) {
  geocountries = json.features;
  gcountries.selectAll('path')
    .data(geocountries)
    .enter().append('path')
      .attr('d', path)
      .on('click', click);

  // draw circles for capitals
  glinks.selectAll('circle')
    .data(geocountries.filter(function(d){
      // ignore countries with missing data for now
      return ('undefined' === typeof capitals[d.id]) ? false : true;
    }))
    .enter().append('circle')
      .attr('cx', function(d) {return projection(capitals[d.id].coords)[0]})
      .attr('cy', function(d) {return projection(capitals[d.id].coords)[1]})
      .attr('r', 1)
      .append('title')
        .text(function(d) {return capitals[d.id].name + ', ' + d.properties.name});

});

})();
