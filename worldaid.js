(function() {

var width = 720,
  height = 540,
  legendh = 100,
  pathopacity = .5,
  selected,
  centered,
  geocountries,
  relation, // Population or GDP
  proj = d3.geo.equirectangular().scale(1).translate([0, 0]),
  arc = d3.geo.greatArc().precision(1),
  centroid = function(d) {return path.centroid(d.geometry)},
  format = d3.format(',d'),
  color = d3.scale.category20(),
  projection = d3.geo.mercator().scale(width).translate([0, 0]),
  path = d3.geo.path().projection(projection)
  // unused
  minarrowwidth = .3;

var tf = function() {
  return 'translate(' + width / 2 + ',' + height / 2 + ')'
};

var svg = d3.select('#map').append('svg')
  .attr('width', width)
  .attr('height', height)
  .call(d3.behavior.zoom().on('zoom', function() {rescale()}))
    .append('svg:g');

svg.append('rect')
  .attr('class', 'background')
  .attr('width', width)
  .attr('height', height);

var gcountries = svg.append('g')
  .attr('transform', tf)
  .append('g')
    .attr('id', 'countries');

var glegend = svg.append('g')
  .attr('transform', 'translate(0,' + (height - legendh) +')')
  .attr('width', width)
  .attr('height', legendh)
  .attr('id', 'legend');
glegend.append('svg:text').text('Legend').attr('class', 'heading');

var garcs = svg.append('g')
  .attr('transform', tf)
  .attr('id', 'arcs');

var linkcoords = function(d) {
  d.source = capitals[d.source];
  d.target = capitals[d.target];
  return d;
};

var dollarval = function(d) {
  var usd = d.usdollars;
  if (relation) usd = usd / d[relation];
  return Math.sqrt(usd) / 10000;
};

var rescale = function() {
  svg.attr('transform', 'translate(' + d3.event.translate + ')'
    + ' scale(' + d3.event.scale + ')')
}

//FIXME use min and max of total
var scalelinks = d3.scale.sqrt().domain([-10000000,10000000]);

//FIXME implement country select
var click = function(d) {
  console.log(d);
}

var drawlinks = function(links) {
  garcs.selectAll('path')
    .data(links)
    .enter().append('path')
      .style('opacity', .5)
      .style('stroke', function(d) {return color(d.source)})
      .style('stroke-width', function(d) {return dollarval(d)})
      .style('fill', 'none')
      .attr('d', function(d) {
        d = linkcoords(d);
        var p = {source:d.source.coords, target:d.target.coords};
        return path(arc(p))
      })
//      .style('fill', function(d) {return color(d.source)})
//      .attr('d', function (d) {
//        var inflow = false;
//        d = linkcoords(d);
//        return curvedarrow(projection(d.source.coords), projection(d.target.coords), inflow, Math.sqrt(d.usdollars) / 1000);
//      })
      .on('mouseover', function(d) {
        garcs.selectAll('path').style('opacity', .1);
        d3.select(this).style('stroke', 'red').style('opacity', pathopacity);
      })
      .on('mouseout', function(d) {
        garcs.selectAll('path').style('opacity', pathopacity);
        d3.select(this).style('stroke', color(d.source));
      })
      .append('title')
        .text(function(d) {return format(d.usdollars) + ' USD from ' + d.source.name + ' to ' + d.target.name});
}

var drawlegend = function(links) {
  glegend.selectAll('text')
    .data(links)
    .enter().append('svg:text')
//      .attr('text-anchor', 'middle')
      .attr('y', function(d, i) {return 10 * i})
      .attr('x', 0)
      .attr('dx', 10)
      .attr('dy', 8)
      .attr('fill', 'red')
      .text(function(d) {console.log(d); return 'Source: ' + d.source.iso});
}

// main program flow
//var current_sources = ['ESP', 'USA', 'DEU'];
var current_sources = ['DEU', 'ESP', 'FRA', 'GBR', 'USA'];
//var current_targets = ['AFG', 'VUT', 'VEN', 'VNM'];
var current_targets = ['VUT'];

selected = donations.filter(function(d){
  return ('undefined' !== typeof capitals[d.source]
    && 'undefined' !== typeof capitals[d.target]
    && -1 !== current_sources.indexOf(d.source)
    //&& -1 !== current_targets.indexOf(d.target)
  ) ? true : false
});

drawlinks(selected);
drawlegend(selected);

d3.json('world-countries.json', function(error, json) { // d3 v3
//d3.json('world-countries.json', function(json) { // d3 v2
  geocountries = json.features;
  gcountries.selectAll('path')
    .data(geocountries)
    .enter().append('path')
      .attr('d', path)
      .on('click', click);

  // draw circles for capitals
  gcountries.selectAll('circle')
    .data(geocountries.filter(function(d){
      // ignore countries with missing data for now
      return ('undefined' === typeof capitals[d.id]) ? false : true;
    }))
    .enter().append('circle')
      .attr('cx', function(d) {return projection(capitals[d.id].coords)[0]})
      .attr('cy', function(d) {return projection(capitals[d.id].coords)[1]})
      .attr('r', 2)
      .append('title')
        .text(function(d) {return capitals[d.id].name + ', ' + d.properties.name});
});

// unused
// adapted from http://www.uis.unesco.org/Education/Pages/international-student-flow-viz.aspx
// inflow / outflow doesn't work
function curvedarrow(src, trg, inflow, width) {
  var arrowOffset = width;

  if (inflow) arrowOffset = -arrowOffset;

  dx = trg[0] - src[0]; //distance between src and trg
  dy = trg[1] - src[1];
  cx = (src[0]+trg[0])/2; //center of the line
  cy = (src[1]+trg[1])/2;

  ra = Math.sqrt(dx * dx + dy * dy);
  er = ra / (Math.abs(dx / height))*.3; //ellipse radius

  //calculating control point according to er
  lineangle = Math.atan(dy/dx); //angle of the line between src and trg
  erangle = Math.asin((ra/2)/er); // angle of the arc

  if (isNaN(erangle)) {
    console.log(src[0], src[1], dx, dy, ra, er, erangle)
    // FIXME arrow will be missing
    return;
  }

  rc = Math.tan(erangle)*(ra/2); // distance between direct line and control point

  cpx = Math.cos(lineangle-(Math.PI/2))*rc; // absolute coordinates of the ctrl point
  cpy = Math.sin(lineangle-(Math.PI/2))*rc;

  ctrx = cpx+cx; //coords of ctrl point relative to direct line
  ctry = cpy+cy;

  trgangle = Math.atan((ctrx-trg[0])/(ctry-trg[1]));
  angle= Math.PI/2; // set the angle so its always bending upwards

  if (trg[0]-src[0] < 0) angle = -Math.PI/2;
  if (trgangle != 0) arrowOffset = -arrowOffset;

  dTrgX = trg[0]+Math.sin(trgangle)*arrowOffset;
  dTrgY = trg[1]+Math.cos(trgangle)*arrowOffset;

  TinX = dTrgX+(Math.sin(trgangle+angle)*width);
  TinY = dTrgY+(Math.cos(trgangle+angle)*width);
  ToutX = dTrgX+(Math.sin(trgangle-angle)*width);
  ToutY = dTrgY+(Math.cos(trgangle-angle)*width);

  curveOut= 'M'+ TinX + "," +TinY+' Q'+ctrx+','+ctry+' '+src[0] + "," + src[1];
  curveIn = ' Q'+ctrx+','+ctry+' '+ToutX + "," + ToutY;
  arrowHead= ' L' +trg[0] + "," + trg[1]+ ' '+ TinX + "," +TinY;

  finalArrow = curveOut + curveIn + arrowHead;
  return finalArrow ;
}

})();
