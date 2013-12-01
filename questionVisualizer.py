import codecs

def produceVisualPage(parts):
    with codecs.open('d3/visual.html', 'w+', 'utf-8') as f:
        f.write(htmlTextSingleQuestion(parts))

# takes the question parts as array
def scriptTextSingleQuestion(parts):

    scriptStr = """<script>                                                             
                     var g = new dagreD3.Digraph();"""


    # adding nodes
    for part in parts:
        partID = part[0]
        partText = part[1]

        # this is for deriv parts like : _ ne (goes to nedir) if
        if partText == "_":
            partText = part[2]

        scriptStr += "g.addNode(" + partID + ", {label: \"" + partText + "\",nodeclass: \"type-TK\"});"


    # adding edges
    for part in parts:
        partID = part[0]
        partRoot = part[6]

        partDepTag = part[7] # like SUBJECT

        scriptStr += "g.addEdge(null," + partID + "," + partRoot + "," + "{label: \"" + partDepTag + "\"});"

        scriptStr += """
  var renderer = new dagreD3.Renderer();
  var oldDrawNode = renderer.drawNode();
  renderer.drawNode(function(graph, u, svg) {
    oldDrawNode(graph, u, svg);
    svg.classed(graph.node(u).nodeclass, true);
  });
  var layout = renderer.run(g, d3.select("svg g"));
  d3.select("svg")
    .attr("width", layout.graph().width + 40)
    .attr("height", layout.graph().height + 40);

  d3.select("svg").call(d3.behavior.zoom().on("zoom", function() {
        var svg = d3.select("svg");
        var ev = d3.event;
        svg.select("g")
          .attr("transform", "translate(" + ev.translate + ") scale(" + ev.scale + ")");
      }));
</script>
"""
    return scriptStr




def htmlTextSingleQuestion(parts):
    htmlStr = """
<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script type="text/javascript" src="resources/dagre-d3.min.js"></script>

<style>
.type-TK > .label > rect {
  fill: #00ffd0;
}

svg {
  border: 1px solid #999;
}

text {
  font-weight: 300;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serf;
  font-size: 14px;
}

rect {
  fill: #fff;
}

.node rect {
  stroke-width: 1px;
  stroke: #999;
  fill: none;
}

.edge rect {
  fill: #fff;
}

.edge path {
  fill: none;
  stroke: #333;
  stroke-width: 1.5px;
}
</style>

<div id="attach">
  <svg id="svg-canvas" width=800 height=600>
    <g transform="translate(20, 20)"/>
  </svg>
</div>

"""

    htmlStr += scriptTextSingleQuestion(parts)

    return htmlStr
