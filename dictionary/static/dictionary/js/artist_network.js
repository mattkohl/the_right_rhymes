/**
* Created by MBK on 03/05/2016.
*/

var w = window.innerWidth,
    h = window.innerHeight,
    maxNodeSize = 50,
    root;

var vis;
var force = d3.layout.force();

vis = d3.select("#vis").append("svg");

var slug = d3.select(".artist_slug").text();
var endpoint = '/artists/' + slug + '/network_json/';

$.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}'},
        function (data) {
            var json = $.parseJSON(data);
            root = json;

            var n = flatten(root),
                maxCollabs = Math.max.apply(Math,n.map(function(d){return d.size;})),
                nLen = n.length;

            d3.select("#numCollabs").text(nLen - 1);

            var adjustment = (Math.sqrt(nLen)*2.5)/Math.sqrt(h);
            if (adjustment < 0.175) adjustment = 0.175;

            if (h < 600) {
                adjustment = adjustment + (nLen * .01) ;
            }
            h = h * adjustment;

            vis.attr("width", w).attr("height", h);

            root.fixed = true;
            root.x = w / 2;
            root.y = h / 2;

            graph();
        }
);

function graph() {
    var nodes = flatten(root),
        links = d3.layout.tree().links(nodes);
    var defs = vis.insert("svg:defs")
            .attr("id", "mdefs");

    defs.data(["end"])
            .enter()
            .append("svg:path")
            .attr("d", "M0,-5L10,0L0,5");

    var patterns = defs.selectAll('pattern')
            .data(nodes)
            .enter()
            .append("svg:pattern")
                .attr('id', function(d) {
                    return hashCode(d.name);
                })
                .attr("width", 2)
                .attr("height", 2)
                .attr("x", 0)
                .attr("y", 0)
                .append("svg:image")
                .attr("xlink:href", function (d) {
                    return d.img;
                })
                .attr("width", function(d){
                    if (d.name === root.name) {
                        return 100
                    } else return Math.sqrt(Math.sqrt(d.size)) * 40;
                })
                .attr("height", function(d) {
                    if (d.name === root.name) {
                        return 100
                    } else return Math.sqrt(Math.sqrt(d.size)) * 40;
                })
                .attr("x", 0)
                .attr("y", 0);

    var update = function() {

        // Restart the force layout.
        force.nodes(nodes)
                .links(links)
                .gravity(0.05)
                .charge(-1500)
                .linkDistance(function(d){
                    return (Math.sqrt(d.target.size) * 35) + 25;
                })
                .friction(0.5)
                .linkStrength(function (l, i) {
                    return 1;
                })
                .size([w, h])
                .on("tick", tick)
                .start();

        var path = vis.selectAll("path.link")
                .data(links, function (d) {
                    return d.target.id;
                });

        path.enter().insert("svg:path")
                .attr("class", "link")
                .style("stroke", "#ccc")
                .style("fill", "transparent")        ;


        // Exit any old paths.
        path.exit().remove();


        // Update the nodes…
        var node = vis.selectAll("g.node")
                .data(nodes, function (d) {
                    return d.id;
                });


        // Enter any new nodes.
        var nodeEnter = node.enter().append("svg:g")
                .attr("class", "node")
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                })
                .on("click",function(d){
                    if (d != root) {
                        var href = d.link;
                        location.href = href;
                    }
                })
                .call(force.drag);

        // Append a circle
        nodeEnter.append("svg:circle")
                .attr("r", function (d) {
                    if (d.name === root.name) {
                        return 50
                    } else return Math.sqrt(Math.sqrt(d.size)) * 20;
                })
                .style("stroke", "black")     // displays small black dot
                .style("stroke-width", 1)
                .style("fill", function(d) {
                    var image = hashCode(d.name);
                    return "url(#" + image + ")";
                })
                .on('mouseenter', function () {
                    // select element in current context
                    d3.select(this)
                            .transition()
                            .attr("x", function (d) {
                                return -60;
                            })
                            .attr("y", function (d) {
                                return -60;
                            })
                            .attr("height", 100)
                            .attr("width", 100)
                            .style("stroke", "#3399FF")     // displays small black dot
                            .style("stroke-width", 3)
                            .style("opacity", 0.9);

                })
                // set back
                .on('mouseleave', function () {
                    d3.select(this)
                            .transition()
                            .attr("x", function (d) {
                                return -25;
                            })
                            .attr("y", function (d) {
                                return -25;
                            })
                            .attr("height", 50)
                            .attr("width", 50)
                            .style("stroke", "black")     // displays small black dot
                            .style("stroke-width", 1)
                            .style("opacity", 1);

                })
                .on("mouseover", function(d){
                    tooltip.text(d.name);
                    tooltip.style("visibility", "visible");

                    if (d.name != root.name) {
                        if (d.size === 1) {
                            tooltipSubtext.text("(" + d.size + " collaboration)");
                        } else {
                            tooltipSubtext.text("(" + d.size + " collaborations)");
                        }
                        tooltipSubtext.style("visibility", "visible");
                    }
                })
                .on("mousemove", function(d){
                    tooltip.style("top",
                        (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+15)+"px");
                    tooltipSubtext.style("top",
                        (d3.event.pageY+15)+"px").style("left",(d3.event.pageX+5)+"px");
                })
                .on("mouseout", function(d){
                    tooltip.style("visibility", "hidden");
                    tooltipSubtext.style("visibility", "hidden");
                });

        var tooltip = d3.select("body")
                .append("div")
                .attr("id", "tooltip")
                .style("position", "absolute")
                .style("z-index", "10")
                .style("visibility", "hidden")
                .style("color", "white")
                .style("text-shadow", "1px 1px 10px black");

        var tooltipSubtext = d3.select("body")
                .append("div")
                .attr("id", "tooltipSubtext")
                .style("position", "absolute")
                .style("z-index", "10")
                .style("visibility", "hidden")
                .style("color", "white")
                .style("font-size", 8)
                .style("text-shadow", "1px 1px 10px black");

        // Exit any old nodes.
        node.exit().remove();


        // Re-select for update.
        path = vis.selectAll("path.link");
        node = vis.selectAll("g.node");

        function tick() {

            path.attr("d", function (d) {

                var dx = d.target.x - d.source.x,
                        dy = d.target.y - d.source.y,
                        dr = Math.sqrt(dx * dx + dy * dy);

                return "M" + d.source.x + ","
                        + d.source.y
                        + "A" + dr + ","
                        + dr + " 0 0,1 "
                        + d.target.x + ","
                        + d.target.y;
            });

            node.attr("transform", nodeTransform);
        }
    };

    function click(d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else {
            d.children = d._children;
            d._children = null;
        }

        update();
    }

    update();
}

/**
 * Gives the coordinates of the border for keeping the nodes inside a frame
 * http://bl.ocks.org/mbostock/1129492
 */
function nodeTransform(d) {
    d.x = Math.max(maxNodeSize, Math.min(w - (Math.sqrt(Math.sqrt(d.size)) * 40), d.x));
    d.y = Math.max(maxNodeSize, Math.min(h - (Math.sqrt(Math.sqrt(d.size)) * 40), d.y));
    return "translate(" + d.x + "," + d.y + ")";
};

/**
 * Returns a list of all nodes under the root.
 */
function flatten(root) {
    var nodes = [];
    var i = 0;

    function recurse(node) {
        if (node.children)
            node.children.forEach(recurse);
        if (!node.id)
            node.id = ++i;
        nodes.push(node);
    }

    recurse(root);
    return nodes;
};

var hashCode = function(s){
    return s.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0);
};


