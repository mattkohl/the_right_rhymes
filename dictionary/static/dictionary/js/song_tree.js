var diameter = 960;

var tree = d3.layout.tree()
    .size([360, diameter / 2 - 120])
    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

var diagonal = d3.svg.diagonal.radial()
    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var svgTree = d3.select("#songTreeVis").append("svg")
    .attr("width", diameter)
    .attr("height", diameter - 150)
  .append("g")
    .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

var slug = d3.select(".song_slug").text();
var endpoint = '/songs/' + slug + '/song_tree/';

$.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}'},
        function (data) {
            var treeJson = $.parseJSON(data);
            treeRoot = treeJson;

            var treeNodes = tree.nodes(treeRoot),
                treeLinks = tree.links(treeNodes);

            var treeLink = svgTree.selectAll(".treeLink")
                .data(treeLinks)
                .enter().append("path")
                .attr("class", "treeLink")
                .attr("d", diagonal);

            var node = svgTree.selectAll(".treeNode")
                .data(treeNodes)
                .enter().append("g")
                .attr("class", "treeNode")
                .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
                .on("click",function(d){
                    if (d != root) {
                        var href = d.link;
                        console.log(href);
                        location.href = href;
                    }
                });

            node.append("circle")
                .attr("r", 4.5);

            node.append("text")
                .attr("dy", ".31em")
                .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
                .text(function(d) { return d.name; });


});

d3.select(self.frameElement).style("height", diameter - 150 + "px");