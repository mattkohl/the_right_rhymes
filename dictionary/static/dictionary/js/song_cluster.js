/**
 * Created by MBK on 18/05/2016.
 */

var width = window.innerWidth,
    height = window.innerHeight;

var cluster = d3.layout.cluster()
    .size([width, height]);

var diagonal = d3.svg.diagonal()
    .projection(function (d) {
        return [d.x, d.y/3];
    });

var initPos = 0;

console.log(width, height, initPos);

var svg = d3.select("#songTreeVis").append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(" + initPos + ", 50)");

var slug = d3.select(".song_slug").text();
var endpoint = '/data/songs/' + slug + '/release_date_tree/';

$.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}'},
        function (data) {

            var treeRoot = data,
                treeNodes = cluster.nodes(treeRoot),
                treeLinks = cluster.links(treeNodes);

            var treeLink = svg.selectAll(".treeLink")
                .data(treeLinks)
                .enter().append("path")
                .attr("class", "treeLink")
                .attr("d", diagonal);

            var treeNode = svg.selectAll(".treeNode")
                .data(treeNodes)
                .enter().append("g")
                .attr("class", function(d) {
                    if (d != treeRoot){
                        return "treeNode"
                    } else {
                        return "treeRoot"
                    }
                })
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y/3 + ")";
                })
                .on("click",function(d){
                    if (d != treeRoot) {
                        location.href = d.link;
                    }
                });

            treeNode.append("circle")
                .attr("r", 4.5);

            treeNode.append("text")
                .attr("dx", function (d) {
                    if (d != treeRoot){
                        return d.children ? -8 : 8;
                    } else {
                        return d.name.length * 4.75;
                    }
                })
                .attr("dy", function (d) {
                    if (d != treeRoot){
                        return 3;
                    } else {
                        return -10;
                    }

                })
                .style("text-anchor", function (d) {
                    return d.children ? "end" : "start";
                })
                .text(function (d) {
                    return d.name;
                })
                .attr("transform", function(d) {
                    if (d != treeRoot){
                        return "rotate(90)"
                    } else {
                        return "rotate(0)"
                    }
                });
        }
);

d3.select(self.frameElement).style("height", height - 150 + "px");