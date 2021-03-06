# -*- coding: utf-8 -*-
import codecs, os


def visualizeAllQuestions(questions):

    htmlStr = '<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8"></head><body><ul>'

    qNumber = 1
    for question in questions:
        
        htmlStr += '<li><a href=\"visual' + str(qNumber) + '.html\">' + question.questionText + '</a></li>'

        produceVisualPage(question.questionParts, question.questionText, qNumber, True)
        qNumber += 1

    htmlStr += '</ul></body></html>'

    with codecs.open('visualizer/d3/all/index.html', 'w+', 'utf-8') as f:
        f.write(htmlStr)

def produceVisualPage(parts, qText, qNumber = 1, qAll = False):

    if qAll:
        if not os.path.exists('visualizer/d3/all/'):
            print('not exists, created')
            os.makedirs('visualizer/d3/all/')

        dirPath = 'visualizer/d3/all/'
    else:
        dirPath = 'visualizer/d3/'

    fName = dirPath + 'visual' + str(qNumber) + '.html'

    with codecs.open(fName, 'w+', 'utf-8') as f:
        f.write(htmlTextSingleQuestion(parts, qText, qAll))

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

        scriptStr += "\n g.addNode(" + partID + ", {label: \"" + partText + "\",nodeclass: \"type-TK\"});"


    # adding edges
    for part in parts:
        partID = part[0]
        partRoot = part[6]

        partDepTag = part[7] # like SUBJECT

        if part[1] == ".":
            continue

        """
        TÜRKÇE HACK BEGIN
        """

        if partDepTag == 'CLASSIFIER':
            turkTag = 'B.SİZ İSİM TAM.'.decode('utf8')
        elif partDepTag == 'SUBJECT':
            turkTag = 'ÖZNE'.decode('utf8')
        elif partDepTag == 'DETERMINER':
            turkTag = 'BELİRTEÇ'.decode('utf8')
        elif partDepTag == 'MODIFIER':
            turkTag = 'SIFAT/ZARF TAM.'.decode('utf8')
        elif partDepTag == 'SENTENCE':
            turkTag = 'YÜKLEM'.decode('utf8')
        elif partDepTag == 'DERIV':
            turkTag = 'TÜREME'.decode('utf8')
        elif partDepTag == 'POSSESSOR':
            turkTag = 'B.Lİ İSİM TAM.'.decode('utf8')
        elif partDepTag == 'DATIVE.ADJUNCT':
            turkTag = 'E HALİ YÖNELME'.decode('utf8')
        elif partDepTag == 'ABLATIVE.ADJUNCT':
            turkTag = 'DEN HALİ'.decode('utf8')
        elif partDepTag == 'LOCATIVE.ADJUNCT':
            turkTag = 'DE HALİ'.decode('utf8')
        elif partDepTag == 'COORDINATION':
            turkTag = 'BAĞLANTI'.decode('utf8')
        elif partDepTag == 'OBJECT':
            turkTag = 'NESNE'.decode('utf8')
        else:
            turkTag = partDepTag
        #scriptStr += "\n g.addEdge(null," + partID + "," + partRoot + "," + "{label: \"" + partDepTag + "\"});"

        scriptStr += "\n g.addEdge(null," + partID + "," + partRoot + "," + "{label: \"" + turkTag + "\"});"

        """
        TÜRKÇE HACK END
        """

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




def htmlTextSingleQuestion(parts, qText, qAll):
    htmlStr = """<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8"><script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>\n"""

    htmlStr += "<script type=\"text/javascript\" src=\""
    if qAll:
        htmlStr += '../resources/dagre-d3.min.js\"></script>'
    else:
        htmlStr += 'resources/dagre-d3.min.js\"></script>'

    htmlStr += """

<style>
.type-TK > .label > rect {
  fill: #00ffd0;
}

svg {
  align:center
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

</head>
<body>

<p>%s</p>

<hr>

<div id="attach">
  <svg id="svg-canvas" width=800 height=600>
    <g transform="translate(20, 20)"/>
  </svg>
</div>

""" % (qText)

    htmlStr += scriptTextSingleQuestion(parts)

    return htmlStr
