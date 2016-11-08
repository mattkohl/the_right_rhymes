var diameter = window.innerWidth * .9;

var tree = d3.layout.tree()
    .size([360, diameter / 2 - 120])
    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

var diagonal = d3.svg.diagonal.radial()
    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var svgTree = d3.select("#songTreeVis").append("svg")
    .attr("width", diameter)
    .attr("height", diameter + 50)
  .append("g")
    .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

var slug = d3.select(".song_slug").text();
var endpoint = '/data/songs/' + slug + '/release_date_tree/';

$.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}'},
        function (data) {
            var treeJson = data,
                treeRoot = treeJson,
                treeNodes = tree.nodes(treeRoot),
                treeLinks = tree.links(treeNodes);

            var treeLink = svgTree.selectAll(".treeLink")
                .data(treeLinks)
                .enter().append("path")
                .attr("class", "treeLink")
                .attr("d", diagonal);

            var node = svgTree.selectAll(".treeNode")
                .data(treeNodes)
                .enter().append("g")
                .attr("class", function(d) {
                    if (d != treeRoot){
                        return "treeNode"
                    } else {
                        return "treeRoot"
                    }
                })
                .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
                .on("click",function(d){
                    if (d != treeRoot) {
                        location.href = d.link;
                    }
                });

            node.append("circle")
                .attr("r", 4.5);

            node.append("text")
                .attr("dy", ".31em")
                .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                .attr("transform", function(d) {
                        return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)";
                })
                .text(function(d) { return d.name; });


});

d3.select(self.frameElement).style("height", diameter - 150 + "px");